from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.pay_reward import PayRewardParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_pool_event


async def on_pay_reward(
    ctx: HandlerContext,
    pay_reward: Transaction[PayRewardParameter, PoolStorage],
) -> None:
    pool_event_id, pool_event_diff = get_pool_event(pay_reward.storage)
    param_event_id = int(pay_reward.parameter.__root__)
    assert pool_event_id == param_event_id, 'wrong updated event_id in diff'
    assert pay_reward.data.amount is not None
    amount = from_mutez(pay_reward.data.amount)

    event = await models.PoolEvent.filter(id=pool_event_id).get()
    event.result = amount  # type: ignore
    await event.save()

    pool_address = pay_reward.data.target_address
    pool = await models.Pool.get(address=pool_address)
    pool.active_liquidity -= (event.provided - event.claimed)
    assert pool.active_liquidity >= 0, 'wrong state: negative active pool liquidity'
    profit_loss = event.result - event.provided

    left_amount = event.provided - event.claimed
    assert left_amount >= 0, 'wrong state: event claimed > provided'
    pool_profit_loss = profit_loss * left_amount / event.provided
    pool.total_liquidity += pool_profit_loss  # type: ignore
    assert pool.total_liquidity >= 0, 'wrong state: negative total liquidity'
    await pool.save()

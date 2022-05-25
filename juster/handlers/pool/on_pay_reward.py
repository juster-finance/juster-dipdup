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
    assert pool_event_id == param_event_id
    assert pay_reward.data.amount is not None
    amount = from_mutez(pay_reward.data.amount)

    event = await models.PoolEvent.filter(id=pool_event_id).get()
    event.result = amount  # type: ignore
    await event.save()

    pool_address = pay_reward.data.target_address
    pool, _ = await models.Pool.get_or_create(address=pool_address)
    profit_loss = event.result - event.provided

    active_shares = event.total_shares - event.locked_shares
    assert active_shares >= 0
    pool_profit_loss = profit_loss * active_shares / event.total_shares
    pool.total_liquidity += pool_profit_loss  # type: ignore
    assert pool.total_liquidity >= 0
    await pool.save()

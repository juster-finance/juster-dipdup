from decimal import Decimal

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.pay_reward import PayRewardParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_pool_event
from juster.utils import update_pool_state


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
    event.result = amount
    await event.save()

    pool_address = pay_reward.data.target_address
    pool = await models.Pool.get(address=pool_address)

    await update_pool_state(
        pool=pool,
        data=pay_reward.data,
        active_liquidity_diff=event.claimed - event.provided,
        withdrawable_liquidity_diff=event.calc_withdrawable(),
        total_liquidity_diff=event.calc_pool_profit_loss(),
    )

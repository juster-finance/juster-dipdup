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
    # TODO: is it OK to access this __root__ or there are any other ways? [3]
    param_event_id = int(pay_reward.parameter.__root__)
    assert pool_event_id == param_event_id
    amount = from_mutez(pay_reward.data.amount)

    event = await models.PoolEvent.filter(id=pool_event_id).get()
    event.result = amount
    await event.save()

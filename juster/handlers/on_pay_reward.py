
from dipdup.models import Transaction
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.pay_reward import PayRewardParameter

async def on_pay_reward(
    ctx: HandlerContext,
    pay_reward: Transaction[PayRewardParameter, PoolStorage],
) -> None:
    ...
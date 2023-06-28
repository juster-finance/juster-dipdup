from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.default import DefaultParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import update_pool_state


async def on_default(
    ctx: HandlerContext,
    default: Transaction[DefaultParameter, PoolStorage],
) -> None:
    if default.data.amount == 0:
        return

    assert default.data.amount
    amount = from_mutez(default.data.amount)
    pool_address = default.data.target_address

    pool = await models.Pool.get(address=pool_address)
    await update_pool_state(
        pool=pool,
        action=models.PoolHistoryAction.RECEIVED_XTZ,
        data=default.data,
        total_liquidity_diff=amount,
    )

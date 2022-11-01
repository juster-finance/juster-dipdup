from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.cancel_liquidity import CancelLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import update_pool_state


async def on_cancel_liquidity(
    ctx: HandlerContext,
    cancel_liquidity: Transaction[CancelLiquidityParameter, PoolStorage],
) -> None:
    entry_id = int(cancel_liquidity.parameter.__root__)
    pool_address = cancel_liquidity.data.target_address
    pool = await models.Pool.get(address=pool_address)

    entry = await models.EntryLiquidity.filter(pool=pool, entry_id=entry_id).get()
    entry.status = models.EntryStatus.CANCELED
    await entry.save()

    user = await entry.user.get()

    await update_pool_state(
        pool=pool,
        action=models.PoolHistoryAction.LIQUIDITY_CANCELED,
        data=cancel_liquidity.data,
        entry_liquidity_diff=-entry.amount,
        affected_user=user,
        affected_entry=entry,
    )

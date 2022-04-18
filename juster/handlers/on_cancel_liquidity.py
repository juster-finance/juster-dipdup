
from dipdup.context import HandlerContext
from juster.types.pool.parameter.cancel_liquidity import CancelLiquidityParameter
from dipdup.models import Transaction
from juster.types.pool.storage import PoolStorage

import juster.models as models


async def on_cancel_liquidity(
    ctx: HandlerContext,
    cancel_liquidity: Transaction[CancelLiquidityParameter, PoolStorage],
) -> None:
    # TODO: is it OK to access this __root__ or there are any other ways? [2]
    entry_id = int(cancel_liquidity.parameter.__root__)
    entry = await models.EntryLiquidity.filter(id=entry_id).get()
    entry.status = models.EntryStatus.CANCELED
    await entry.save()


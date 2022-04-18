
from dipdup.context import HandlerContext
from juster.types.pool.parameter.cancel_liquidity import CancelLiquidityParameter
from dipdup.models import Transaction
from juster.types.pool.storage import PoolStorage

async def on_cancel_liquidity(
    ctx: HandlerContext,
    cancel_liquidity: Transaction[CancelLiquidityParameter, PoolStorage],
) -> None:
    ...
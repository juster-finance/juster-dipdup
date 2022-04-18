
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from dipdup.models import Transaction
from juster.types.pool.parameter.claim_liquidity import ClaimLiquidityParameter

async def on_claim_liquidity(
    ctx: HandlerContext,
    claim_liquidity: Transaction[ClaimLiquidityParameter, PoolStorage],
) -> None:
    ...
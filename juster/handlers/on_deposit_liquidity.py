
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from dipdup.models import Transaction
from juster.types.pool.parameter.deposit_liquidity import DepositLiquidityParameter

async def on_deposit_liquidity(
    ctx: HandlerContext,
    deposit_liquidity: Transaction[DepositLiquidityParameter, PoolStorage],
) -> None:
    ...
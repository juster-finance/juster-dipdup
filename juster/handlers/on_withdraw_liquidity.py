
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.withdraw_liquidity import WithdrawLiquidityParameter
from dipdup.models import Transaction

async def on_withdraw_liquidity(
    ctx: HandlerContext,
    withdraw_liquidity: Transaction[WithdrawLiquidityParameter, PoolStorage],
) -> None:
    ...
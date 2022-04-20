
from dipdup.context import HandlerContext
from dipdup.models import Transaction
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.default import DefaultParameter

async def on_default(
    ctx: HandlerContext,
    default: Transaction[DefaultParameter, PoolStorage],
) -> None:
    ...
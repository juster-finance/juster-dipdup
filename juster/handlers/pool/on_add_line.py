
from dipdup.context import HandlerContext
from dipdup.models import Transaction
from juster.types.pool.parameter.add_line import AddLineParameter
from juster.types.pool.storage import PoolStorage

async def on_add_line(
    ctx: HandlerContext,
    add_line: Transaction[AddLineParameter, PoolStorage],
) -> None:
    ...
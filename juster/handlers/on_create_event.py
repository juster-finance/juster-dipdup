
from dipdup.models import Transaction
from juster.types.pool.parameter.create_event import CreateEventParameter
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage

async def on_create_event(
    ctx: HandlerContext,
    create_event: Transaction[CreateEventParameter, PoolStorage],
) -> None:
    ...
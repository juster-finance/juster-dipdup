
from juster.types.pool.storage import PoolStorage
from dipdup.context import HandlerContext
from juster.types.pool.parameter.disband import DisbandParameter
from dipdup.models import Transaction

async def on_disband(
    ctx: HandlerContext,
    disband: Transaction[DisbandParameter, PoolStorage],
) -> None:
    ...
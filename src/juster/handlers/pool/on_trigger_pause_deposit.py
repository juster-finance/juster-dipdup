
from juster.types.pool.storage import PoolStorage
from dipdup.context import HandlerContext
from juster.types.pool.parameter.trigger_pause_deposit import TriggerPauseDepositParameter
from dipdup.models import Transaction

async def on_trigger_pause_deposit(
    ctx: HandlerContext,
    trigger_pause_deposit: Transaction[TriggerPauseDepositParameter, PoolStorage],
) -> None:
    ...
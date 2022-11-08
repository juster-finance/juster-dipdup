
from juster.types.pool.parameter.trigger_pause_line import TriggerPauseLineParameter
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from dipdup.models import Transaction

async def on_trigger_pause_line(
    ctx: HandlerContext,
    trigger_pause_line: Transaction[TriggerPauseLineParameter, PoolStorage],
) -> None:
    ...
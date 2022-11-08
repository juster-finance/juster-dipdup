from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.trigger_pause_line import TriggerPauseLineParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import get_line
from juster.utils import update_pool_state


async def on_trigger_pause_line(
    ctx: HandlerContext,
    trigger_pause_line: Transaction[TriggerPauseLineParameter, PoolStorage],
) -> None:

    line_id, line_diff = get_line(trigger_pause_line.storage)
    pool_address = trigger_pause_line.data.target_address
    pool = await models.Pool.get(address=pool_address)
    line = await models.PoolLine.get(pool=pool, line_id=line_id)

    assert line.is_paused != line_diff.isPaused, 'pause state was not changed'
    line.is_paused = line_diff.isPaused
    await line.save()

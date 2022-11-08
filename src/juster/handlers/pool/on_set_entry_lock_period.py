from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.set_entry_lock_period import SetEntryLockPeriodParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import update_pool_state


async def on_set_entry_lock_period(
    ctx: HandlerContext,
    set_entry_lock_period: Transaction[SetEntryLockPeriodParameter, PoolStorage],
) -> None:

    pool_address = set_entry_lock_period.data.target_address
    pool = await models.Pool.get(address=pool_address)
    new_period = int(set_entry_lock_period.storage.entryLockPeriod)
    pool.entry_lock_period = new_period
    await pool.save()

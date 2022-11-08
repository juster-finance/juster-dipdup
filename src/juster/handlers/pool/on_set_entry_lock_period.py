
from juster.types.pool.storage import PoolStorage
from dipdup.context import HandlerContext
from juster.types.pool.parameter.set_entry_lock_period import SetEntryLockPeriodParameter
from dipdup.models import Transaction

async def on_set_entry_lock_period(
    ctx: HandlerContext,
    set_entry_lock_period: Transaction[SetEntryLockPeriodParameter, PoolStorage],
) -> None:
    ...
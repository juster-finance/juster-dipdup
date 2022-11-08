from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.trigger_pause_deposit import TriggerPauseDepositParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import update_pool_state


async def on_trigger_pause_deposit(
    ctx: HandlerContext,
    trigger_pause_deposit: Transaction[TriggerPauseDepositParameter, PoolStorage],
) -> None:

    pool_address = trigger_pause_deposit.data.target_address
    pool = await models.Pool.get(address=pool_address)

    is_deposit_paused = trigger_pause_deposit.storage.isDepositPaused
    assert pool.is_deposit_paused != is_deposit_paused, 'pause state was not changed'

    pool.is_deposit_paused = is_deposit_paused
    await pool.save()

    action = (
        models.PoolHistoryAction.DEPOSITS_PAUSED if is_deposit_paused
        else models.PoolHistoryAction.DEPOSITS_UNPAUSED
    )

    await update_pool_state(
        pool=pool,
        action=action,
        data=trigger_pause_deposit.data,
    )

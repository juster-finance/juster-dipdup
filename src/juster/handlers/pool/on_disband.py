from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.disband import DisbandParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import update_pool_state


async def on_disband(
    ctx: HandlerContext,
    disband: Transaction[DisbandParameter, PoolStorage],
) -> None:
    assert disband.storage.isDisbandAllow is True
    pool_address = disband.data.target_address
    pool = await models.Pool.get(address=pool_address)
    pool.is_disband_allow = True
    await pool.save()

    await update_pool_state(
        pool=pool,
        action=models.PoolHistoryAction.POOL_DISBANDED,
        data=disband.data,
    )

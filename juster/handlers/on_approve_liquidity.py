
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.approve_liquidity import ApproveLiquidityParameter
from dipdup.models import Transaction

import juster.models as models
from juster.utils import (
    get_position,
    get_entry,
    process_pool_shares
)


async def on_approve_liquidity(
    ctx: HandlerContext,
    approve_liquidity: Transaction[ApproveLiquidityParameter, PoolStorage],
) -> None:

    position_id, position_diff = get_position(approve_liquidity.storage)
    sender = approve_liquidity.data.sender_address
    user, _ = await models.User.get_or_create(address=sender)
    shares = process_pool_shares(position_diff.shares)
    assert shares > 0

    position = models.PoolPosition(
        id=position_id,
        user=user,
        shares=shares,
    )
    await position.save()

    # TODO: need to understand is it OK to access this __root__ or there are any other ways?
    entry_id = int(approve_liquidity.parameter.__root__)
    entry = await models.EntryLiquidity.filter(id=entry_id).get()
    entry.status = models.EntryStatus.APPROVED
    await entry.save()


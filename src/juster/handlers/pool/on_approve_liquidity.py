from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.approve_liquidity import ApproveLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import get_position
from juster.utils import process_pool_shares
from juster.utils import update_pool_state


async def on_approve_liquidity(
    ctx: HandlerContext,
    approve_liquidity: Transaction[ApproveLiquidityParameter, PoolStorage],
) -> None:

    position_id, position_diff = get_position(approve_liquidity.storage)
    provider = position_diff.provider
    user, _ = await models.User.get_or_create(address=provider)
    shares = process_pool_shares(position_diff.shares)
    assert shares > 0, 'wrong state: approve liquidity with 0 shares diff'

    pool_address = approve_liquidity.data.target_address
    pool = await models.Pool.get(address=pool_address)

    entry_id = int(approve_liquidity.parameter.__root__)
    entry = await models.EntryLiquidity.filter(entry_id=entry_id, pool=pool).get()
    assert entry.status == models.EntryStatus.PENDING, 'unexpected entry status'
    entry.status = models.EntryStatus.APPROVED
    await entry.save()

    position = models.PoolPosition(
        pool_position_id=f'{pool.address}-{position_id}',
        pool=pool,
        position_id=position_id,
        entry=entry,
        user=user,
        shares=shares,
        entry_share_price=entry.amount / shares,
    )
    await position.save()

    await update_pool_state(
        pool=pool,
        data=approve_liquidity.data,
        total_liquidity_diff=entry.amount,
        entry_liquidity_diff=-entry.amount,
        total_shares_diff=shares,
    )

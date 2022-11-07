from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.approve_entry import ApproveEntryParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import get_shares
from juster.utils import process_pool_shares
from juster.utils import update_pool_state


async def on_approve_entry(
    ctx: HandlerContext,
    approve_entry: Transaction[ApproveEntryParameter, PoolStorage],
) -> None:

    provider, shares = get_shares(approve_entry.storage)
    user, _ = await models.User.get_or_create(address=provider)
    assert shares > 0, 'wrong state: approve liquidity with 0 shares diff'

    pool_address = approve_entry.data.target_address
    pool = await models.Pool.get(address=pool_address)

    entry_id = int(approve_entry.parameter.__root__)
    entry = await models.EntryLiquidity.filter(entry_id=entry_id, pool=pool).get()
    assert entry.status == models.EntryStatus.PENDING, 'unexpected entry status'
    entry.status = models.EntryStatus.APPROVED
    await entry.save()

    position, _ = await models.PoolPosition.get_or_create(
        user=user, pool=pool, defaults={'entry': entry, 'entry_share_price': entry.amount / shares}
    )
    position.shares += shares
    await position.save()

    await update_pool_state(
        pool=pool,
        action=models.PoolHistoryAction.LIQUIDITY_APPROVED,
        data=approve_entry.data,
        total_liquidity_diff=entry.amount,
        entry_liquidity_diff=-entry.amount,
        total_shares_diff=shares,
        affected_user=user,
        affected_entry=entry,
    )

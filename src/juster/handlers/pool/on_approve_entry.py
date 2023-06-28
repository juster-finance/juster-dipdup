from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.approve_entry import ApproveEntryParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import get_shares
from juster.utils import update_pool_state


async def on_approve_entry(
    ctx: HandlerContext,
    approve_entry: Transaction[ApproveEntryParameter, PoolStorage],
) -> None:
    provider, new_shares = get_shares(approve_entry.storage)

    user, _ = await models.User.get_or_create(address=provider)

    pool_address = approve_entry.data.target_address
    pool = await models.Pool.get(address=pool_address)

    entry_id = int(approve_entry.parameter.__root__)
    entry = await models.EntryLiquidity.filter(entry_id=entry_id, pool=pool).get()
    assert entry.status == models.EntryStatus.PENDING, 'unexpected entry status'
    entry.status = models.EntryStatus.APPROVED

    position, _ = await models.PoolPosition.get_or_create(user=user, pool=pool, defaults={'entry': entry})
    # TODO: is there any way to check that onchain was exactly the same diff?
    added_shares = new_shares - position.shares
    assert added_shares >= 0, 'wrong state: approve liquidity with negative shares diff'

    position.shares += added_shares
    position.deposited_amount += entry.amount

    # TODO: is it required to calculate entry share price on serverside?
    shares_sum = position.shares + position.withdrawn_shares
    position.entry_share_price = position.deposited_amount / shares_sum
    await position.save()

    entry.position = position
    await entry.save()

    await update_pool_state(
        pool=pool,
        action=models.PoolHistoryAction.LIQUIDITY_APPROVED,
        data=approve_entry.data,
        total_liquidity_diff=entry.amount,
        entry_liquidity_diff=-entry.amount,
        total_shares_diff=added_shares,
        affected_user=user,
        affected_entry=entry,
    )

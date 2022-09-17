from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.deposit_liquidity import DepositLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_entry
from juster.utils import parse_datetime
from juster.utils import update_pool_state


async def on_deposit_liquidity(
    ctx: HandlerContext,
    deposit_liquidity: Transaction[DepositLiquidityParameter, PoolStorage],
) -> None:
    sender = deposit_liquidity.data.sender_address
    user, _ = await models.User.get_or_create(address=sender)
    assert deposit_liquidity.data.amount
    assert len(deposit_liquidity.storage.entries) == 1

    entry_id, entry_diff = get_entry(deposit_liquidity.storage)
    amount = from_mutez(deposit_liquidity.data.amount)

    pool_address = deposit_liquidity.data.target_address
    pool = await models.Pool.get(address=pool_address)

    entry = models.EntryLiquidity(
        pool_entry_id=f'{pool.address}-{entry_id}',
        pool=pool,
        entry_id=entry_id,
        user=user,
        accept_time=parse_datetime(entry_diff.acceptAfter),
        amount=amount,
        status=models.EntryStatus.PENDING,
    )
    await entry.save()

    await update_pool_state(
        pool=pool,
        data=deposit_liquidity.data,
        entry_liquidity_diff=amount,
    )

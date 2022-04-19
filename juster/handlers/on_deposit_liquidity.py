from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.deposit_liquidity import DepositLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_entry
from juster.utils import parse_datetime


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

    entry = models.EntryLiquidity(
        id=entry_id,
        user=user,
        accept_time=parse_datetime(entry_diff.acceptAfter),
        amount=amount,
        status=models.EntryStatus.PENDING
    )
    await entry.save()

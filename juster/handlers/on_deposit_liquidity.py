
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from dipdup.models import Transaction
from juster.types.pool.parameter.deposit_liquidity import DepositLiquidityParameter

import juster.models as models
from juster.utils import parse_datetime
from juster.utils import from_mutez


async def on_deposit_liquidity(
    ctx: HandlerContext,
    deposit_liquidity: Transaction[DepositLiquidityParameter, PoolStorage],
) -> None:
    user, _ = await models.User.get_or_create(address=deposit_liquidity.data.sender_address)
    assert deposit_liquidity.data.amount
    assert len(deposit_liquidity.storage.entries) == 1
    entry_id = int(next(iter(deposit_liquidity.storage.entries)))
    entry_diff = deposit_liquidity.storage.entries[str(entry_id)]
    amount = from_mutez(deposit_liquidity.data.amount)

    entry = models.EntryLiquidity(
        id=entry_id,
        user=user,
        accept_time=parse_datetime(entry_diff.acceptAfter),
        amount=amount
    )
    await entry.save()


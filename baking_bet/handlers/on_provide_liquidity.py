from dipdup.models import Transaction
from dipdup.context import OperationHandlerContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.provide_liquidity import ProvideLiquidityParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import get_event, from_mutez


async def on_provide_liquidity(
    ctx: OperationHandlerContext,
    provide_liquidity: Transaction[ProvideLiquidityParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(provide_liquidity.storage)
    assert provide_liquidity.data.amount
    amount = from_mutez(provide_liquidity.data.amount)

    event = await models.Event.filter(id=event_id).get()
    new_liquidity_shares = from_mutez(event_diff.totalLiquidityShares)
    liquidity_shares_added = new_liquidity_shares - event.total_liquidity_shares
    event.total_liquidity_shares = new_liquidity_shares  # type: ignore
    event.pool_above_eq = from_mutez(event_diff.poolAboveEq)  # type: ignore
    event.pool_below = from_mutez(event_diff.poolBellow)  # type: ignore
    event.total_liquidity_provided += amount  # type: ignore
    await event.save()

    user, _ = await models.User.get_or_create(address=provide_liquidity.data.sender_address)
    user.total_liquidity_provided += amount  # type: ignore
    await user.save()

    position, _ = await models.Position.get_or_create(
        event=event,
        user=user,
    )
    position.shares += liquidity_shares_added  # type: ignore
    await position.save()

    await models.Deposit(
        event=event,
        user=user,
        amount=amount,
        shares=liquidity_shares_added,
    ).save()

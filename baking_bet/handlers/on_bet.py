from dipdup.models import OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.bet import BetParameter, BetItem
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez, get_event

BetAgainst = BetItem

async def on_bet(
    ctx: OperationHandlerContext,
    bet: TransactionContext[BetParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(bet.storage)
    amount = from_mutez(bet.data.amount)

    event = await models.Event.filter(id=event_id).get()
    event.pool_for = from_mutez(event_diff.poolFor)  # type: ignore
    event.pool_against = from_mutez(event_diff.poolAgainst)  # type: ignore
    event.total_bets_amount += amount  # type: ignore
    await event.save()

    user, _ = await models.User.get_or_create(address=bet.data.sender_address)
    user.total_bets_count += 1  # type: ignore
    user.total_bets_amount += amount  # type: ignore
    await user.save()

    position, _ = await models.Position.get_or_create(
        event=event,
        user=user,
    )
    if isinstance(bet.parameter.bet, BetAgainst):
        assert len(bet.storage.betsAgainst) == 1
        reward = from_mutez(bet.storage.betsAgainst[0].value)
        position.reward_against = reward
        bet_side = models.BetSide.AGAINST
    else:
        assert len(bet.storage.betsFor) == 1
        reward = from_mutez(bet.storage.betsFor[0].value)
        position.reward_for = reward
        bet_side = models.BetSide.FOR
    position.shares += amount / (event.pool_for + event.pool_against)
    await position.save()

    await models.Bet(
        event=event,
        user=user,
        amount=amount,
        reward=reward,
        side=bet_side
    ).save()

    positions = await event.positions
    for position in positions:
        position.reward_for = (position.shares / event.total_liquidity_shares) * event.pool_for
        position.reward_against = (position.shares / event.total_liquidity_shares) * event.pool_against

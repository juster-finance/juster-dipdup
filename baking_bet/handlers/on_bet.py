from dipdup.models import OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.bet import BetParameter, BetItem
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez, get_event

BetAboveEq = BetItem

async def on_bet(
    ctx: OperationHandlerContext,
    bet: TransactionContext[BetParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(bet.storage)
    assert bet.data.amount
    amount = from_mutez(bet.data.amount)

    event = await models.Event.filter(id=event_id).get()
    event.pool_above_eq = from_mutez(event_diff.poolAboveEq)  # type: ignore
    # FIXME: Report typo in storage
    event.pool_below = from_mutez(event_diff.poolBellow)  # type: ignore
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
    if isinstance(bet.parameter.bet, BetAboveEq):
        assert len(bet.storage.betsAboveEq) == 1
        reward = from_mutez(bet.storage.betsAboveEq[0].value)
        bet_reward = reward - position.reward_above_eq
        position.reward_above_eq = reward  # type: ignore
        bet_side = models.BetSide.ABOVE_EQ
    else:
        assert len(bet.storage.betsBellow) == 1
        reward = from_mutez(bet.storage.betsBellow[0].value)
        bet_reward = reward - position.reward_below
        position.reward_below = reward  # type: ignore
        bet_side = models.BetSide.BELOW

    await position.save()

    await models.Bet(
        event=event,
        user=user,
        amount=amount,
        reward=bet_reward,
        side=bet_side
    ).save()

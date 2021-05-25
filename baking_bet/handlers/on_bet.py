from dipdup.models import OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.bet import BetParameter, BetItem
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez, get_event


async def on_bet(
    ctx: OperationHandlerContext,
    bet: TransactionContext[BetParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(bet.storage)
    amount = from_mutez(bet.data.amount)

    event = await models.Event.filter(id=event_id).get()
    event.poolFor = from_mutez(event_diff.poolFor)  # type: ignore
    event.poolAgainst = from_mutez(event_diff.poolAgainst)  # type: ignore
    event.totalBetsAmount += amount  # type: ignore
    await event.save()

    user, _ = await models.User.get_or_create(address=bet.data.sender_address)
    user.totalBetsCount += 1  # type: ignore
    user.totalBetsAmount += amount  # type: ignore
    await user.save()

    position, _ = await models.Position.get_or_create(
        event=event,
        user=user,
    )
    if isinstance(bet.parameter.bet, BetItem):
        assert len(bet.storage.betsAgainst) == 1
        reward = from_mutez(bet.storage.betsAgainst[0].value)
        position.rewardAgainst += reward
        bet_side = models.BetSide.AGAINST
    else:
        assert len(bet.storage.betsFor) == 1
        reward = from_mutez(bet.storage.betsFor[0].value)
        position.rewardFor += reward
        bet_side = models.BetSide.FOR
    await position.save()

    await models.Bet(
        event=event,
        user=user,
        amount=amount,
        reward=reward,
        side=bet_side
    ).save()

    # TODO: update all positions with shares (reward for/against based on total shares/provided)

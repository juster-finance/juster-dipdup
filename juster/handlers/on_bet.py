from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.bet import BetItem, BetParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez, get_event

BetAboveEq = BetItem


async def on_bet(
    ctx: HandlerContext,
    bet: Transaction[BetParameter, JusterStorage],
) -> None:
    event_id, event_diff = get_event(bet.storage)
    assert bet.data.amount
    amount = from_mutez(bet.data.amount)

    event = await models.Event.filter(id=event_id).get()
    event.pool_above_eq = from_mutez(event_diff.poolAboveEq)  # type: ignore
    event.pool_below = from_mutez(event_diff.poolBelow)  # type: ignore
    event.total_bets_amount += amount  # type: ignore
    event.total_value_locked += amount  # type: ignore
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
        assert len(bet.storage.betsBelow) == 1
        reward = from_mutez(bet.storage.betsBelow[0].value)
        bet_reward = reward - position.reward_below
        position.reward_below = reward  # type: ignore
        bet_side = models.BetSide.BELOW
    await position.save()

    await models.Bet(
        opg_hash=bet.data.hash,
        created_time=bet.data.timestamp,
        event=event,
        user=user,
        amount=amount,
        reward=bet_reward,
        side=bet_side
    ).save()

    currency_pair = await event.currency_pair
    currency_pair.total_volume += amount  # type: ignore
    currency_pair.total_value_locked += amount  # type: ignore
    await currency_pair.save()

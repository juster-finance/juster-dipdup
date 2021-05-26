from typing import List
from dipdup.models import OperationData, OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.close_callback import CloseCallbackParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez, get_event


async def on_close(
    ctx: OperationHandlerContext,
    close_callback: TransactionContext[CloseCallbackParameter, BetsStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(close_callback.storage)

    event = await models.Event.filter(id=event_id).get()
    event.closed_rate = models.to_ratio(event_diff.closedRate)  # type: ignore
    event.closed_oracle_time = event_diff.closedOracleTime  # type: ignore
    event.closed_dynamics = event.closed_rate / event.start_rate
    event.status = models.EventStatus.FINISHED

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)
    await fee_collector.save()

    higher_target = event.target_dynamics > 1
    lower_target = event.target_dynamics < 1
    equal_target = event.target_dynamics == 1

    higher_target_reached = event.closed_dynamics > event.target_dynamics
    lower_target_reached = event.closed_dynamics < event.target_dynamics
    equal_target_reached = event.closed_dynamics != event.target_dynamics

    if (higher_target and higher_target_reached) or (lower_target and lower_target_reached) or (equal_target and equal_target_reached):
        event.winner_bets = models.BetSide.FOR
    else:
        event.winner_bets = models.BetSide.AGAINST

    await event.save()

    positions: List[models.Position] = await event.positions
    for position in positions:
        user: models.User = await position.user
        shares_percentage = (position.shares / event.total_liquidity_shares)
        pool = event.pool_for if event.winner_bets == models.BetSide.FOR else event.pool_against
        reward = pool * shares_percentage
        user.total_reward += reward
        await user.save()

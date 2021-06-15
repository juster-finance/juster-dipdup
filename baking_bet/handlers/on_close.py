from dipdup.models import OperationData, Transaction
from dipdup.context import OperationHandlerContext
from typing import List

import baking_bet.models as models

from baking_bet.types.bets.parameter.close_callback import CloseCallbackParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez, get_event


async def on_close(
    ctx: OperationHandlerContext,
    close_callback: Transaction[CloseCallbackParameter, BetsStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(close_callback.storage)

    event = await models.Event.filter(id=event_id).get()
    event.closed_rate = models.to_ratio(event_diff.closedRate)  # type: ignore
    event.closed_oracle_time = event_diff.closedOracleTime  # type: ignore
    event.closed_dynamics = event.closed_rate / event.start_rate  # type: ignore
    event.status = models.EventStatus.FINISHED

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)  # type: ignore
    await fee_collector.save()

    event.set_winner_bets()
    await event.save()

    positions: List[models.Position] = await event.positions
    for position in positions:
        user: models.User = await position.user

        reward = position.get_reward(event.winner_bets)
        user.total_reward += reward  # type: ignore

        if position.shares:
            position.set_shares_reward(event)
            await position.save()
            user.total_reward += position.shares_reward  # type: ignore

        await user.save()

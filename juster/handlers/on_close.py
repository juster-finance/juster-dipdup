from dipdup.models import OperationData, Transaction
from dipdup.context import HandlerContext
from typing import List
import juster.models as models

from juster.types.juster.parameter.close_callback import CloseCallbackParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez, get_event, parse_datetime


async def on_close(
    ctx: HandlerContext,
    close_callback: Transaction[CloseCallbackParameter, JusterStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(close_callback.storage)

    event = await models.Event.filter(id=event_id).get()
    event.closed_rate = models.to_ratio(event_diff.closedRate)  # type: ignore
    event.closed_oracle_time = parse_datetime(event_diff.closedOracleTime)  # type: ignore
    event.closed_dynamics = event.closed_rate / event.start_rate  # type: ignore
    event.status = models.EventStatus.FINISHED

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)  # type: ignore
    await fee_collector.save()

    event.set_winner_bets()
    await event.save()

    positions: List[models.Position] = await event.positions
    for position in positions:
        reward = position.get_reward(event.winner_bets)
        provider_reward = position.get_provider_reward(event.winner_bets, event)
        position.value = reward + provider_reward
        await position.save()

        user: models.User = await position.user
        user.total_reward += reward  # type: ignore
        user.total_provider_reward += provider_reward  # type: ignore
        await user.save()

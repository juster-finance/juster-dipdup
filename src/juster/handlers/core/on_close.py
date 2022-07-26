from typing import List

from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.close_callback import CloseCallbackParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez
from juster.utils import get_event
from juster.utils import parse_datetime


async def on_close(
    ctx: HandlerContext,
    close_callback: Transaction[CloseCallbackParameter, JusterStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(close_callback.storage)

    assert event_diff.closedOracleTime is not None
    assert fee_tx.amount is not None

    event = await models.Event.filter(id=event_id).get()
    event.closed_rate = models.to_ratio(event_diff.closedRate)
    event.closed_oracle_time = parse_datetime(event_diff.closedOracleTime)
    event.closed_dynamics = event.closed_rate / event.start_rate
    event.status = models.EventStatus.FINISHED

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)
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
        user.total_reward += reward
        user.total_provider_reward += provider_reward
        await user.save()

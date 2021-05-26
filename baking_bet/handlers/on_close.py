from dipdup.models import OperationData, OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.close_callback import CloseCallbackParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import get_event


async def on_close(
    ctx: OperationHandlerContext,
    close_callback: TransactionContext[CloseCallbackParameter, BetsStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(close_callback.storage)

    event = await models.Event.filter(id=event_id).get()
    event.closed_rate = models.to_ratio(event_diff.closedRate)  # type: ignore
    event.closed_oracle_time = event_diff.closedOracleTime  # type: ignore
    event.status = models.EventStatus.FINISHED
    await event.save()

    # TODO: Update all users (totalReward)

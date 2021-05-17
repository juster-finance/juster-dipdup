from typing import Optional

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.close_callback import CloseCallbackParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez
from typing import cast
from dateutil.parser import parse

async def on_close(
    ctx: OperationHandlerContext,
    close_callback: TransactionContext[CloseCallbackParameter, BetsStorage],
    transaction_1: OperationData,
) -> None:
    updated_event = close_callback.storage.events[0].value
    event_id = close_callback.storage.events[0].key
    event = await models.Event.filter(id=event_id).get()
    event.closedDynamics = updated_event.closedDynamics  # type: ignore
    event.closedOracleTime = parse(updated_event.closedOracleTime)  # type: ignore
    event.closedRate = updated_event.closedRate  # type: ignore
    event.isBetsForWin = updated_event.isBetsForWin  # type: ignore
    event.isClosed = updated_event.isClosed  # type: ignore
    await event.save()

    user, _ = await models.User.get_or_create(address=transaction_1.target_address)
    user.totalFeesCollected += from_mutez(cast(int, transaction_1.amount))  # type: ignore
    await user.save()

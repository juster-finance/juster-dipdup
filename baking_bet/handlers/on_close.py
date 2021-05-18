from decimal import Decimal
from typing import Optional, cast

from dateutil.parser import parse
from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import demo_bets.models as models
from demo_bets.types.bets.parameter.close_callback import CloseCallbackParameter
from demo_bets.types.bets.storage import BetsStorage
from demo_bets.utils import from_mutez

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
    event.closedDynamics = models.to_dynamics(updated_event.closedDynamics)  # type: ignore
    event.closedOracleTime = parse(updated_event.closedOracleTime)  # type: ignore
    event.closedRate = models.to_ratio(updated_event.closedRate)  # type: ignore
    event.isBetsForWin = updated_event.isBetsForWin  # type: ignore
    event.status = models.EventStatus.FINISHED
    await event.save()

    user, _ = await models.User.get_or_create(address=transaction_1.target_address)
    user.totalFeesCollected += from_mutez(cast(int, transaction_1.amount))  # type: ignore
    await user.save()

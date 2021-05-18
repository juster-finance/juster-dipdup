from decimal import Decimal
from typing import Optional, cast
from baking_bet.utils import from_mutez

from dateutil.parser import parse
from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import baking_bet.models as models
from baking_bet.types.bets.parameter.start_measurement_callback import StartMeasurementCallbackParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez
import baking_bet.models as models
from dateutil.parser import parse
from baking_bet.types.bets.parameter.start_measurement_callback import StartMeasurementCallbackParameter
from baking_bet.types.bets.storage import BetsStorage



async def on_start_measurement(
    ctx: OperationHandlerContext,
    start_measurement_callback: TransactionContext[StartMeasurementCallbackParameter, BetsStorage],
    transaction_0: OperationData,
) -> None:
    updated_event = start_measurement_callback.storage.events[0].value
    event_id = start_measurement_callback.storage.events[0].key
    event = await models.Event.filter(id=event_id).get()
    event.measureOracleStartTime = parse(updated_event.measureOracleStartTime)  # type: ignore
    event.startRate = models.to_ratio(updated_event.startRate)
    event.status = models.EventStatus.ACTIVE
    await event.save()

    user, _ = await models.User.get_or_create(address=transaction_0.target_address)
    user.totalFeesCollected += from_mutez(cast(int, transaction_0.amount))  # type: ignore

from dipdup.models import OperationData, OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.start_measurement_callback import StartMeasurementCallbackParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez, get_event


async def on_start_measurement(
    ctx: OperationHandlerContext,
    start_measurement_callback: TransactionContext[StartMeasurementCallbackParameter, BetsStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(start_measurement_callback.storage)

    event = await models.Event.filter(id=event_id).get()
    event.measure_oracle_start_time = event_diff.measureOracleStartTime  # type: ignore
    event.start_rate = models.to_ratio(event_diff.startRate)
    event.status = models.EventStatus.STARTED
    await event.save()

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)
    await fee_collector.save()

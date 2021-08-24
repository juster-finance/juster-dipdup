from dipdup.models import OperationData, Transaction
from dipdup.context import HandlerContext
from datetime import datetime
import juster.models as models

from juster.types.juster.parameter.start_measurement_callback import StartMeasurementCallbackParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez, get_event, parse_datetime


async def on_start_measurement(
    ctx: HandlerContext,
    start_measurement_callback: Transaction[StartMeasurementCallbackParameter, JusterStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(start_measurement_callback.storage)

    event = await models.Event.filter(id=event_id).get()
    event.measure_oracle_start_time = parse_datetime(event_diff.measureOracleStartTime)  # type: ignore
    event.start_rate = models.to_ratio(event_diff.startRate)
    event.status = models.EventStatus.STARTED
    await event.save()

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)  # type: ignore
    await fee_collector.save()

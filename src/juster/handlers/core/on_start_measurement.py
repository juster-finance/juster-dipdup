from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.start_measurement_callback import StartMeasurementCallbackParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez
from juster.utils import get_event
from juster.utils import parse_datetime


async def on_start_measurement(
    ctx: HandlerContext,
    start_measurement_callback: Transaction[StartMeasurementCallbackParameter, JusterStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(start_measurement_callback.storage)

    assert event_diff.measureOracleStartTime is not None
    assert fee_tx.amount is not None

    event = await models.Event.filter(id=event_id).get()
    event.measure_oracle_start_time = parse_datetime(event_diff.measureOracleStartTime)
    event.start_rate = models.to_ratio(event_diff.startRate)
    event.status = models.EventStatus.STARTED
    await event.save()

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)
    await fee_collector.save()

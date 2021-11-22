from dipdup.context import HandlerContext
from dipdup.models import OperationData, Transaction

import juster.models as models
from juster.types.juster.parameter.trigger_force_majeure import TriggerForceMajeureParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez, get_event


async def on_force_majeure(
    ctx: HandlerContext,
    trigger_force_majeure: Transaction[TriggerForceMajeureParameter, JusterStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(trigger_force_majeure.storage)

    event = await models.Event.filter(id=event_id).get()
    event.status = models.EventStatus.CANCELED
    await event.save()

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)  # type: ignore
    await fee_collector.save()

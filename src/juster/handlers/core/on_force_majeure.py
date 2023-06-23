from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.trigger_force_majeure import TriggerForceMajeureParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez
from juster.utils import get_event


async def on_force_majeure(
    ctx: HandlerContext,
    trigger_force_majeure: Transaction[TriggerForceMajeureParameter, JusterStorage],
    fee_tx: OperationData,
) -> None:
    event_id, event_diff = get_event(trigger_force_majeure.storage)

    assert fee_tx.amount is not None

    event = await models.Event.filter(id=event_id).get()
    event.status = models.EventStatus.CANCELED
    await event.save()

    fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
    fee_collector.total_fees_collected += from_mutez(fee_tx.amount)
    await fee_collector.save()

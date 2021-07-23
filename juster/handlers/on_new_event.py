from dipdup.models import Transaction
from dipdup.context import HandlerContext

import juster.models as models

from juster.types.juster.parameter.new_event import NewEventParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import get_event


async def on_new_event(
    ctx: HandlerContext,
    new_event: Transaction[NewEventParameter, JusterStorage],
) -> None:
    event_id, event_diff = get_event(new_event.storage)

    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=event_diff.currencyPair)
    currency_pair.total_events += 1  # type: ignore
    await currency_pair.save()

    creator, _ = await models.User.get_or_create(address=new_event.data.sender_address)
    await creator.save()

    event = models.Event(
        id=event_id,
        creator=creator,
        currency_pair=currency_pair,
        status=models.EventStatus.NEW,
        target_dynamics=models.to_dynamics(event_diff.targetDynamics),
        measure_period=int(event_diff.measurePeriod),
        bets_close_time=event_diff.betsCloseTime,
        start_rate=None,
        liquidity_percent=models.to_liquidity(event_diff.liquidityPercent),
    )
    await event.save()

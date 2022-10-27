from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.new_event import NewEventParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import get_event
from juster.utils import parse_datetime


async def on_new_event(
    ctx: HandlerContext,
    new_event: Transaction[NewEventParameter, JusterStorage],
) -> None:
    event_id, event_diff = get_event(new_event.storage)

    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=event_diff.currencyPair)
    currency_pair.total_events += 1
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
        bets_close_time=parse_datetime(event_diff.betsCloseTime),
        created_time=parse_datetime(event_diff.createdTime),
        start_rate=None,
        liquidity_percent=models.to_liquidity(event_diff.liquidityPercent),
    )
    await event.save()

    # As far as this handler runs after pool.on_create_event handler, pool_event
    # created before event creation and it is bounded to event here:
    pool_event = await models.PoolEvent.get_or_none(id=event_id)
    if pool_event is not None:
        pool_event.event = event
        await pool_event.save()

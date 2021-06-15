from dipdup.models import Transaction
from dipdup.context import OperationHandlerContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.new_event import NewEventParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import get_event


async def on_new_event(
    ctx: OperationHandlerContext,
    new_event: Transaction[NewEventParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(new_event.storage)

    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=event_diff.currencyPair)

    event = models.Event(
        id=event_id,
        currency_pair=currency_pair,
        status=models.EventStatus.NEW,
        target_dynamics=models.to_dynamics(event_diff.targetDynamics),
        measure_period=int(event_diff.measurePeriod),
        bets_close_time=event_diff.betsCloseTime,
        start_rate=None,
        liquidity_percent=models.to_liquidity(event_diff.liquidityPercent)
    )
    await event.save()

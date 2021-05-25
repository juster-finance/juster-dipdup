from dipdup.models import OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.new_event import NewEventParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import get_event


async def on_new_event(
    ctx: OperationHandlerContext,
    new_event: TransactionContext[NewEventParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(new_event.storage)

    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=event_diff.currencyPair)

    event = models.Event(
        id=event_id,
        currencyPair=currency_pair,
        status=models.EventStatus.NEW,
        targetDynamics=models.to_dynamics(event_diff.targetDynamics),
        measurePeriod=int(event_diff.measurePeriod),
        betsCloseTime=event_diff.betsCloseTime,
        startRate=models.to_ratio(event_diff.startRate),
        liquidityPercent=models.to_liquidity(event_diff.liquidityPercent)
    )
    await event.save()

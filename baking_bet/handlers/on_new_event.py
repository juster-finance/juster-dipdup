from decimal import Decimal
from typing import Optional
from baking_bet.utils import from_mutez

from dateutil.parser import parse
from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import baking_bet.models as models
from baking_bet.types.bets.parameter.new_event import NewEventParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez
import baking_bet.models as models

from baking_bet.types.bets.parameter.new_event import NewEventParameter
from baking_bet.types.bets.storage import BetsStorage


async def on_new_event(
    ctx: OperationHandlerContext,
    new_event: TransactionContext[NewEventParameter, BetsStorage],
) -> None:
    user, _ = await models.User.get_or_create(address=new_event.data.sender_address)
    id_ = new_event.storage.events[0].key
    event = new_event.storage.events[0].value
    symbol, _ = await models.Symbol.get_or_create(symbol=event.currencyPair)
    event_model = models.Event(
        id=id_,
        betsAgainstLiquidityPoolSum=from_mutez(event.betsAgainstLiquidityPoolSum),
        betsCloseTime=event.betsCloseTime,
        betsForLiquidityPoolSum=from_mutez(event.betsForLiquidityPoolSum),
        closedDynamics=models.to_dynamics(event.closedDynamics),
        closedOracleTime=parse(event.closedOracleTime),
        closedRate=models.to_ratio(event.closedRate),
        createdTime=event.createdTime,
        currencyPair=symbol,
        expirationFee=from_mutez(event.expirationFee),
        firstProviderAgainstSharesSum=from_mutez(event.firstProviderAgainstSharesSum),
        firstProviderForSharesSum=from_mutez(event.firstProviderForSharesSum),
        isBetsForWin=event.isBetsForWin,
        liquidityPercent=models.to_liquidity(event.liquidityPercent),
        measureOracleStartTime=event.measureOracleStartTime,
        measurePeriod=event.measurePeriod,
        measureStartFee=from_mutez(event.measureStartFee),
        oracleAddress=event.oracleAddress,
        rewardCallFee=from_mutez(event.rewardCallFee),
        startRate=models.to_ratio(event.startRate),
        targetDynamics=models.to_dynamics(event.targetDynamics),
        totalLiquidityAgainstSharesSum=from_mutez(event.totalLiquidityAgainstSharesSum),
        totalLiquidityForSharesSum=from_mutez(event.totalLiquidityForSharesSum),
        totalLiquidityProvided=from_mutez(event.totalLiquidityProvided),
        winAgainstProfitLossPerShare=models.to_share(event.winAgainstProfitLossPerShare),
        winForProfitLossPerShare=models.to_share(event.winForProfitLossPerShare),
        user=user,
        status=models.EventStatus.NEW,
    )
    await event_model.save()

    user.totalEventsCreated += 1  # type: ignore
    await user.save()

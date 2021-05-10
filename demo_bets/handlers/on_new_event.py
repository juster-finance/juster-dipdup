from typing import Optional
from demo_bets.utils import from_mutez

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import demo_bets.models as models

from demo_bets.types.bets.parameter.new_event import NewEventParameter
from demo_bets.types.bets.storage import BetsStorage

from dateutil.parser import parse\

async def on_new_event(
    ctx: OperationHandlerContext,
    new_event: TransactionContext[NewEventParameter, BetsStorage],
) -> None:
    user, _ = await models.User.get_or_create(address=new_event.data.sender_address)
    id_ = new_event.storage.events[0].key
    event = new_event.storage.events[0].value
    event_model = models.Event(
        id=id_,
        betsAgainstLiquidityPoolSum=from_mutez(event.betsAgainstLiquidityPoolSum),
        betsCloseTime=event.betsCloseTime,
        betsForLiquidityPoolSum=from_mutez(event.betsForLiquidityPoolSum),
        closedDynamics=event.closedDynamics,
        closedOracleTime=parse(event.closedOracleTime),
        closedRate=event.closedRate,
        createdTime=event.createdTime,
        currencyPair=event.currencyPair,
        expirationFee=from_mutez(event.expirationFee),
        firstProviderAgainstSharesSum=from_mutez(event.firstProviderAgainstSharesSum),
        firstProviderForSharesSum=from_mutez(event.firstProviderForSharesSum),
        isBetsForWin=event.isBetsForWin,
        isClosed=event.isClosed,
        isMeasurementStarted=event.isMeasurementStarted,
        liquidityPercent=event.liquidityPercent,
        liquidityPrecision=event.liquidityPrecision,
        measureOracleStartTime=event.measureOracleStartTime,
        measurePeriod=event.measurePeriod,
        measureStartFee=from_mutez(event.measureStartFee),
        oracleAddress=event.oracleAddress,
        ratioPrecision=event.ratioPrecision,
        rewardCallFee=from_mutez(event.rewardCallFee),
        sharePrecision=event.sharePrecision,
        startRate=event.startRate,
        targetDynamics=event.targetDynamics,
        targetDynamicsPrecision=event.targetDynamicsPrecision,
        totalLiquidityAgainstSharesSum=from_mutez(event.totalLiquidityAgainstSharesSum),
        totalLiquidityForSharesSum=from_mutez(event.totalLiquidityForSharesSum),
        totalLiquidityProvided=from_mutez(event.totalLiquidityProvided),
        winAgainstProfitLossPerShare=event.winAgainstProfitLossPerShare,
        winForProfitLossPerShare=event.winForProfitLossPerShare,

        user=user,
    )
    await event_model.save()

    user.totalEventsCreated += 1  # type: ignore
    await user.save()

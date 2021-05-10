from typing import Optional, cast

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import demo_bets.models as models

from demo_bets.types.bets.parameter.bet import BetParameter
from demo_bets.types.bets.storage import BetsForWinningLedgerItem, BetsStorage
from demo_bets.utils import from_mutez

async def on_bet(
    ctx: OperationHandlerContext,
    bet: TransactionContext[BetParameter, BetsStorage],
) -> None:
    updated_event = bet.storage.events[0].value
    event_id = bet.storage.events[0].key
    event = await models.Event.filter(id=event_id).get()
    event.betsAgainstLiquidityPoolSum = from_mutez(updated_event.betsAgainstLiquidityPoolSum)  # type: ignore
    event.betsForLiquidityPoolSum = from_mutez(updated_event.betsForLiquidityPoolSum)  # type: ignore
    event.winAgainstProfitLossPerShare=int(updated_event.winAgainstProfitLossPerShare)  # type: ignore
    event.winForProfitLossPerShare=int(updated_event.winForProfitLossPerShare)  # type: ignore

    user, _ = await models.User.get_or_create(address=bet.data.sender_address)
    args = dict(depositedBets=from_mutez(bet.storage.depositedBets[0].value))
    amount = from_mutez(cast(int, bet.data.amount))
    if bet.storage.betsAgainstWinningLedger:
        args['betsAgainstWinningLedger'] = from_mutez(bet.storage.betsAgainstWinningLedger[0].value)
        is_for = False
        event.totalBetsAgainst += 1  # type: ignore
    if bet.storage.betsForWinningLedger:
        args['betsForWinningLedger'] = from_mutez(bet.storage.betsForWinningLedger[0].value)
        is_for = True
        event.totalBetsFor += 1  # type: ignore
    await event.save()

    await models.Bet(
        event=event,
        user=user,
        amount=amount,
        isFor=is_for,
    ).save()

    await models.Ledger.update_or_create(
        event=event,
        user=user,
        defaults=args,
    )

    user.totalBets += 1  # type: ignore
    user.totalDepositedBets += amount  # type: ignore
    await user.save()

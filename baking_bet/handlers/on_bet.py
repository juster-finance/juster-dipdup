from decimal import Decimal
from typing import Optional, cast

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import baking_bet.models as models
from baking_bet.types.bets.parameter.bet import BetParameter
from baking_bet.types.bets.storage import BetsForWinningLedgerItem, BetsStorage
from baking_bet.utils import from_mutez
import baking_bet.models as models

from baking_bet.types.bets.parameter.bet import BetParameter
from baking_bet.types.bets.storage import BetsForWinningLedgerItem, BetsStorage
from baking_bet.utils import from_mutez


async def on_bet(
    ctx: OperationHandlerContext,
    bet: TransactionContext[BetParameter, BetsStorage],
) -> None:
    updated_event = bet.storage.events[0].value
    event_id = bet.storage.events[0].key
    event = await models.Event.filter(id=event_id).get()
    event.betsAgainstLiquidityPoolSum = from_mutez(updated_event.betsAgainstLiquidityPoolSum)  # type: ignore
    event.betsForLiquidityPoolSum = from_mutez(updated_event.betsForLiquidityPoolSum)  # type: ignore
    event.winAgainstProfitLossPerShare = models.to_share(updated_event.winAgainstProfitLossPerShare)  # type: ignore
    event.winForProfitLossPerShare = models.to_share(updated_event.winForProfitLossPerShare)  # type: ignore

    user, _ = await models.User.get_or_create(address=bet.data.sender_address)
    amount = from_mutez(cast(int, bet.data.amount))

    ledger, _ = await models.Ledger.get_or_create(
        event=event,
        user=user,
    )
    ledger.depositedBets = from_mutez(bet.storage.depositedBets[0].value)

    if bet.storage.betsAgainstWinningLedger:
        new_reward = from_mutez(bet.storage.betsAgainstWinningLedger[0].value)
        reward = new_reward - ledger.betsAgainstWinningLedger
        ledger.betsAgainstWinningLedger = new_reward
        is_for = False
        event.totalBetsAgainst += 1  # type: ignore
    if bet.storage.betsForWinningLedger:
        new_reward = from_mutez(bet.storage.betsForWinningLedger[0].value)
        reward = new_reward - ledger.betsForWinningLedger
        ledger.betsAgainstWinningLedger = new_reward
        is_for = True
        event.totalBetsFor += 1  # type: ignore
    await event.save()
    await ledger.save()

    await models.Bet(
        event=event,
        user=user,
        amount=amount,
        reward=reward,
        isFor=is_for,
    ).save()

    user.totalBets += 1  # type: ignore
    user.totalDepositedBets += amount  # type: ignore
    await user.save()

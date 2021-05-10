from typing import Optional

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import demo_bets.models as models
from demo_bets.utils import from_mutez
from demo_bets.types.bets.parameter.withdraw import WithdrawParameter
from demo_bets.types.bets.storage import BetsStorage
from typing import cast


async def on_withdraw(
    ctx: OperationHandlerContext,
    withdraw: TransactionContext[WithdrawParameter, BetsStorage],
    transaction_2: OperationData,
) -> None:
    event_id = withdraw.storage.events[0].key
    event = await models.Event.filter(id=event_id).get()

    user, _ = await models.User.get_or_create(address=transaction_2.target_address)
    user.totalWithdrawed += from_mutez(cast(int, transaction_2.amount))  # type: ignore
    await user.save()

    ledger = await models.Ledger.filter(event=event, user=user).get()
    ledger.withdrawed = True  # type: ignore
    await ledger.save()

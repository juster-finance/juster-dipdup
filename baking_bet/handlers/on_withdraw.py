from dipdup.models import OperationData, Transaction
from dipdup.context import OperationHandlerContext


import baking_bet.models as models

from baking_bet.types.bets.parameter.withdraw import WithdrawParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez


async def on_withdraw(
    ctx: OperationHandlerContext,
    withdraw: Transaction[WithdrawParameter, BetsStorage],
    withdraw_tx: OperationData,
) -> None:
    event_id = int(withdraw.parameter.eventId)
    assert withdraw_tx.amount
    amount = from_mutez(withdraw_tx.amount)

    event = await models.Event.filter(id=event_id).get()

    user, _ = await models.User.get_or_create(address=withdraw.data.sender_address)
    user.total_withdrawn += amount
    await user.save()

    position = await models.Position.filter(event=event, user=user).get()
    position.withdrawn = True
    await position.save()

    await models.Withdrawal(
        event=event,
        user=user,
        amount=amount
    ).save()

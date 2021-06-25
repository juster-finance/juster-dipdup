from dipdup.models import OperationData, Transaction
from dipdup.context import HandlerContext


import juster.models as models

from juster.types.juster.parameter.withdraw import WithdrawParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez


async def on_withdraw(
    ctx: HandlerContext,
    withdraw: Transaction[WithdrawParameter, JusterStorage],
    withdraw_tx: OperationData,
) -> None:
    event_id = int(withdraw.parameter.eventId)
    assert withdraw_tx.amount
    amount = from_mutez(withdraw_tx.amount)

    event = await models.Event.filter(id=event_id).get()

    user, _ = await models.User.get_or_create(address=withdraw.parameter.participantAddress)
    user.total_withdrawn += amount  # type: ignore
    await user.save()

    position = await models.Position.filter(event=event, user=user).get()
    position.withdrawn = True  # type: ignore
    await position.save()

    await models.Withdrawal(
        event=event,
        user=user,
        amount=amount
    ).save()

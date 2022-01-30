from typing import Optional

from dipdup.context import HandlerContext
from dipdup.models import OperationData, Transaction

import juster.models as models
from juster.types.juster.parameter.withdraw import WithdrawParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez


async def on_withdraw(
    ctx: HandlerContext,
    withdraw: Transaction[WithdrawParameter, JusterStorage],
    tx_1: Optional[OperationData] = None,
    tx_2: Optional[OperationData] = None,
) -> None:
    event_id = int(withdraw.parameter.eventId)

    withdraw_tx: Optional[OperationData]
    fee_tx: Optional[OperationData]
    if tx_2 is not None:
        assert tx_1
        assert tx_2.target_address == withdraw.parameter.participantAddress
        assert tx_1.target_address == withdraw.data.sender_address
        withdraw_tx = tx_2
        fee_tx = tx_1
    elif tx_1 is not None:
        assert tx_1.target_address == withdraw.parameter.participantAddress
        withdraw_tx = tx_1
        fee_tx = None
    else:
        withdraw_tx = None
        fee_tx = None

    event = await models.Event.filter(id=event_id).get()
    currency_pair = await event.currency_pair

    position = await models.Position.filter(event=event, user_id=withdraw.parameter.participantAddress).get_or_none()
    if position:
        position.withdrawn = True  # type: ignore
        await position.save()

    if withdraw_tx:
        assert withdraw_tx.amount
        amount = from_mutez(withdraw_tx.amount)
        currency_pair.total_value_locked -= amount  # type: ignore

        user, _ = await models.User.get_or_create(address=withdraw.parameter.participantAddress)
        user.total_withdrawn += amount  # type: ignore

        withdrawal = models.Withdrawal(
            opg_hash=withdraw.data.hash,
            created_time=withdraw.data.timestamp,
            event=event,
            user=user,
            amount=amount,
        )

        if fee_tx:
            # NOTE: Withdrawals initiated by third-parties are rewarded
            assert fee_tx.amount
            amount = from_mutez(fee_tx.amount)
            currency_pair.total_value_locked -= amount  # type: ignore

            fee_collector, _ = await models.User.get_or_create(address=fee_tx.target_address)
            fee_collector.total_fees_collected += amount  # type: ignore

            withdrawal.fee_collector = fee_collector
            withdrawal.type = models.WithdrawalType.THIRD_PARTY

            await fee_collector.save()
        else:
            withdrawal.type = models.WithdrawalType.MANUAL

        await user.save()
        await withdrawal.save()

    await currency_pair.save()

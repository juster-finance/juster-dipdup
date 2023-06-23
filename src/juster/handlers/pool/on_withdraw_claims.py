from decimal import Decimal
from typing import Dict

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.withdraw_claims import WithdrawClaimsParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import high_precision
from juster.utils import mutez
from juster.utils import quantize_down
from juster.utils import update_pool_state


async def on_withdraw_claims(
    ctx: HandlerContext,
    withdraw_claims: Transaction[WithdrawClaimsParameter, PoolStorage],
) -> None:
    claims = withdraw_claims.parameter.__root__
    rewards: Dict[str, Decimal] = {}

    pool_address = withdraw_claims.data.target_address
    pool = await models.Pool.get(address=pool_address)

    for claim_key in claims:
        event_id = int(claim_key.eventId)
        event = await models.PoolEvent.filter(id=event_id).get()
        user = await models.User.get(address=claim_key.provider)
        position = await models.PoolPosition.filter(pool=pool, user=user).get()
        claim = await models.Claim.filter(pool=pool, event=event, user=user).get()
        claim.withdrawn = True  # type: ignore
        reward = quantize_down(event.result * claim.amount / event.provided, high_precision)
        position.withdrawn_amount += reward
        position.realized_profit += reward - claim.amount
        position.locked_estimate_amount -= claim.amount
        assert position.locked_estimate_amount >= Decimal(0), 'wrong state: negative estimated claims'
        await position.save()
        await claim.save()

        rewards[user.address] = rewards.get(user.address, Decimal(0)) + reward

        await update_pool_state(
            pool=pool,
            action=models.PoolHistoryAction.USER_WITHDRAWN,
            data=withdraw_claims.data,
            withdrawable_liquidity_diff=-reward,
            affected_user=user,
            affected_claim=claim,
            affected_event=event,
        )

    def calc_dust(amount: Decimal) -> Decimal:
        return amount - quantize_down(amount, mutez)

    # and one more updated state with dust diff (which is not related to single positions):
    dust = Decimal(sum(calc_dust(amt) for amt in rewards.values()))
    if dust > Decimal(0):
        await update_pool_state(
            pool=pool,
            action=models.PoolHistoryAction.ACCUMULATED_DUST,
            data=withdraw_claims.data,
            total_liquidity_diff=dust,
        )

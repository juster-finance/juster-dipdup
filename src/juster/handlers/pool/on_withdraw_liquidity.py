from decimal import Decimal
from typing import Dict

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.withdraw_liquidity import WithdrawLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import mutez
from juster.utils import quantize_down


async def on_withdraw_liquidity(
    ctx: HandlerContext,
    withdraw_liquidity: Transaction[WithdrawLiquidityParameter, PoolStorage],
) -> None:
    claims = withdraw_liquidity.parameter.__root__
    rewards: Dict[str, Decimal] = {}

    for claim_key in claims:
        event = await models.PoolEvent.filter(id=int(claim_key.eventId)).get()
        position = await models.PoolPosition.filter(id=int(claim_key.positionId)).get()
        claim = await models.Claim.filter(event=event, position=position).get()
        claim.withdrawn = True
        await claim.save()

        user = await claim.user.get()
        reward = event.result * claim.amount / event.provided
        rewards[user.address] = rewards.get(user.address, Decimal(0)) + reward

    def calc_dust(amount: Decimal) -> Decimal:
        return amount - quantize_down(amount, mutez)

    dust = sum([calc_dust(amt) for amt in rewards.values()])
    pool = await models.Pool.get(address=withdraw_liquidity.data.target_address)
    pool.total_liquidity += dust
    await pool.save()

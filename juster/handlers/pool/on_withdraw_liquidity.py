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

    pool_address = withdraw_liquidity.data.target_address
    pool = await models.Pool.get(address=pool_address)

    for claim_key in claims:
        event_id = int(claim_key.eventId)
        event = await models.PoolEvent.filter(id=event_id).get()
        position_id = int(claim_key.positionId)
        position = await models.PoolPosition.filter(pool=pool, position_id=position_id).get()
        claim = await models.Claim.filter(pool=pool, event=event, position=position).get()
        claim.withdrawn = True  # type: ignore
        await claim.save()

        user = await claim.user.get()  # type: ignore
        reward = event.result * claim.amount / event.provided
        rewards[user.address] = rewards.get(user.address, Decimal(0)) + reward

    def calc_dust(amount: Decimal) -> Decimal:
        return amount - quantize_down(amount, mutez)

    dust = sum([calc_dust(amt) for amt in rewards.values()])
    pool.total_liquidity += dust  # type: ignore
    await pool.save()

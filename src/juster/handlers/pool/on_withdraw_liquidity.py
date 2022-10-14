from decimal import Decimal
from typing import Dict

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.withdraw_liquidity import WithdrawLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import high_precision
from juster.utils import mutez
from juster.utils import quantize_down
from juster.utils import update_pool_state


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
        position.realized_profit += event.calc_profit_loss() * claim.amount / event.provided
        await claim.save()

        user = await claim.user.get()  # type: ignore
        reward = quantize_down(event.result * claim.amount / event.provided, high_precision)
        rewards[user.address] = rewards.get(user.address, Decimal(0)) + reward

    def calc_dust(amount: Decimal) -> Decimal:
        return amount - quantize_down(amount, mutez)

    dust = Decimal(sum(calc_dust(amt) for amt in rewards.values()))
    withdrawn = Decimal(sum(amt for amt in rewards.values()))

    await update_pool_state(
        pool=pool,
        data=withdraw_liquidity.data,
        total_liquidity_diff=dust,
        withdrawable_liquidity_diff=-withdrawn,
    )

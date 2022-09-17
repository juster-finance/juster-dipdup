from decimal import Decimal
from typing import Optional

from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.claim_liquidity import ClaimLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_position
from juster.utils import mutez
from juster.utils import process_pool_shares
from juster.utils import quantize_down
from juster.utils import quantize_up
from juster.utils import update_pool_state


async def on_claim_liquidity(
    ctx: HandlerContext,
    claim_liquidity: Transaction[ClaimLiquidityParameter, PoolStorage],
    transaction_1: Optional[OperationData] = None,
) -> None:

    pool_address = claim_liquidity.data.target_address
    pool = await models.Pool.get(address=pool_address)
    pool_state = await pool.get_last_state()

    position_id, position_diff = get_position(claim_liquidity.storage)
    position = await models.PoolPosition.filter(pool=pool, position_id=position_id).get()
    new_shares = process_pool_shares(position_diff.shares)
    param_shares = process_pool_shares(claim_liquidity.parameter.shares)
    claimed_shares = position.shares - new_shares
    assert claimed_shares == param_shares, 'wrong position shares diff'
    position.shares -= claimed_shares  # type: ignore
    assert position.shares >= 0, 'wrong state: negative shares in position'
    await position.save()

    claimed_fraction = claimed_shares / pool_state.total_shares
    user = await position.user.get()  # type: ignore
    claimed_sum = Decimal(0)

    for claim_pair in claim_liquidity.storage.claims:
        assert position_id == int(claim_pair.key.positionId), 'wrong position_id in added claim'
        assert claim_liquidity.data.sender_address == claim_pair.value.provider, 'wrong provider address in added claim'

        event_id = int(claim_pair.key.eventId)
        event = await models.PoolEvent.filter(id=event_id).get()
        event_active = event.provided - event.claimed

        claimed = quantize_up(event_active * claimed_fraction, mutez)
        claimed_sum += claimed
        event.claimed += claimed  # type: ignore
        await event.save()

        claim, _ = await models.Claim.get_or_create(
            pool=pool, event=event, position=position, defaults={'amount': 0, 'user': user, 'withdrawn': False}
        )
        claim.amount += claimed  # type: ignore
        assert claim.amount == process_pool_shares(claim_pair.value.amount), 'wrong claim shares calculation'
        await claim.save()

    free_liquidity = pool_state.total_liquidity - pool_state.active_liquidity
    payout = quantize_down(free_liquidity * claimed_fraction, mutez)

    if transaction_1 is not None:
        assert transaction_1.amount
        assert payout == from_mutez(transaction_1.amount)

    await update_pool_state(
        pool=pool,
        data=claim_liquidity.data,
        total_liquidity_diff=-claimed_sum - payout,
        active_liquidity_diff=-claimed_sum,
        total_shares_diff=-claimed_shares,
    )

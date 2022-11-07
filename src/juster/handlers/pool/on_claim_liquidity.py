from decimal import Decimal
from typing import Optional

from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.claim_liquidity import ClaimLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_shares
from juster.utils import mutez
from juster.utils import process_pool_shares
from juster.utils import quantize_down
from juster.utils import quantize_up
from juster.utils import update_pool_state


def calc_realized_profit(
    last_pool_state: models.PoolState,
    position: models.PoolPosition,
    claimed_shares: Decimal,
) -> Decimal:
    return (last_pool_state.share_price - position.entry_share_price) * claimed_shares


async def on_claim_liquidity(
    ctx: HandlerContext,
    claim_liquidity: Transaction[ClaimLiquidityParameter, PoolStorage],
    transaction_1: Optional[OperationData] = None,
) -> None:

    pool_address = claim_liquidity.data.target_address
    pool = await models.Pool.get(address=pool_address)
    pool_state = await pool.get_last_state()

    provider, new_shares = get_shares(claim_liquidity.storage)
    param_provider = claim_liquidity.parameter.provider
    assert provider == param_provider, 'wrong provider address in added claim'

    user = await models.User.get(address=provider)
    position = await models.PoolPosition.filter(pool=pool, user=user).get()
    param_shares = process_pool_shares(claim_liquidity.parameter.shares)
    claimed_shares = position.shares - new_shares
    assert claimed_shares == param_shares, 'wrong position shares diff'
    position.realized_profit += calc_realized_profit(pool_state, position, claimed_shares)
    position.shares -= claimed_shares
    assert position.shares >= 0, 'wrong state: negative shares in position'
    position.withdrawn_shares += claimed_shares

    claimed_fraction = claimed_shares / pool_state.total_shares
    user = await position.user.get()  # type: ignore
    claimed_sum = Decimal(0)

    for claim_pair in claim_liquidity.storage.claims:
        assert provider == claim_pair.key.provider, 'wrong provider address in added claim'
        event_id = int(claim_pair.key.eventId)
        event = await models.PoolEvent.filter(id=event_id).get()
        event_active = event.provided - event.claimed

        claimed = quantize_up(event_active * claimed_fraction, mutez)
        claimed_sum += claimed
        event.claimed += claimed
        await event.save()

        claim, _ = await models.Claim.get_or_create(
            pool=pool, event=event, user=user, defaults={'amount': 0, 'position': position, 'withdrawn': False}
        )
        claim.amount += claimed
        assert claim.amount == process_pool_shares(claim_pair.value), 'wrong claim shares calculation'
        await claim.save()

    free_liquidity = pool_state.total_liquidity - pool_state.active_liquidity
    payout = quantize_down(free_liquidity * claimed_fraction, mutez)
    position.withdrawn_amount += payout
    await position.save()

    if transaction_1 is not None:
        assert transaction_1.amount
        assert payout == from_mutez(transaction_1.amount)

    await update_pool_state(
        pool=pool,
        action=models.PoolHistoryAction.USER_CLAIMED,
        data=claim_liquidity.data,
        total_liquidity_diff=-claimed_sum - payout,
        active_liquidity_diff=-claimed_sum,
        total_shares_diff=-claimed_shares,
        affected_user=user,
    )

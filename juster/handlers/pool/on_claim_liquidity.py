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
from juster.utils import process_pool_shares


async def on_claim_liquidity(
    ctx: HandlerContext,
    claim_liquidity: Transaction[ClaimLiquidityParameter, PoolStorage],
    transaction_1: Optional[OperationData] = None,
) -> None:
    position_id, position_diff = get_position(claim_liquidity.storage)
    position = await models.PoolPosition.filter(id=position_id).get()
    new_shares = process_pool_shares(position_diff.shares)
    param_shares = process_pool_shares(claim_liquidity.parameter.shares)
    claimed_shares = position.shares - new_shares
    assert claimed_shares == param_shares, 'wrong position shares diff'
    position.shares -= claimed_shares  # type: ignore
    assert position.shares >= 0, 'wrong state: negative shares in position'
    await position.save()

    user = await position.user.get()  # type: ignore

    claimed_active_liquidity = Decimal(0)

    # withdrawn total liquidity consists of active and free liquidity
    # active_liquidity_fraction + free_liquidity_fraction = 1
    active_liquidity_fraction = Decimal(0)

    for claim_pair in claim_liquidity.storage.claims:
        assert position_id == int(claim_pair.key.positionId), 'wrong position_id in added claim'
        assert claim_liquidity.data.sender_address == claim_pair.value.provider, 'wrong provider address in added claim'

        event_id = int(claim_pair.key.eventId)
        event = await models.PoolEvent.filter(id=event_id).get()
        event.locked_shares += claimed_shares  # type: ignore
        await event.save()

        claim, _ = await models.Claim.get_or_create(
            event=event, position=position, defaults={'shares': 0, 'user': user, 'withdrawn': False}
        )
        claim.shares += claimed_shares  # type: ignore
        assert claim.shares == process_pool_shares(claim_pair.value.shares), 'wrong claim shares calculation'
        await claim.save()

        claimed_active_liquidity += event.provided * claimed_shares / event.total_shares
        active_liquidity_fraction += event.shares / event.total_shares

    free_liquidity_fraction = Decimal(1) - active_liquidity_fraction
    assert free_liquidity_fraction >= Decimal(0), 'wrong state: active liquidity fraction > 100%'

    pool_address = claim_liquidity.data.target_address
    pool, _ = await models.Pool.get_or_create(address=pool_address)

    claimed_volume = claimed_shares * pool.total_liquidity / pool.total_shares
    claimed_free_liquidity = claimed_volume * free_liquidity_fraction

    pool.total_liquidity -= claimed_active_liquidity  # type: ignore

    if transaction_1 is not None:
        assert transaction_1.amount
        payout = from_mutez(transaction_1.amount)
        assert abs(payout - claimed_free_liquidity) <= Decimal('0.000001')

        pool.total_liquidity -= payout  # type: ignore

    assert pool.total_liquidity >= 0, 'wrong state: negative total pool liquidity'
    pool.total_shares -= claimed_shares  # type: ignore
    assert pool.total_shares >= 0, 'wrong state: negative total pool shares'
    await pool.save()

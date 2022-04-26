from decimal import Decimal

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.claim_liquidity import ClaimLiquidityParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_active_events
from juster.utils import get_position
from juster.utils import process_pool_shares


async def on_claim_liquidity(
    ctx: HandlerContext,
    claim_liquidity: Transaction[ClaimLiquidityParameter, PoolStorage],
) -> None:
    position_id, position_diff = get_position(claim_liquidity.storage)
    position = await models.PoolPosition.filter(id=position_id).get()
    new_shares = process_pool_shares(position_diff.shares)
    param_shares = process_pool_shares(claim_liquidity.parameter.shares)
    claimed_shares = position.shares - new_shares
    assert claimed_shares == param_shares

    position.shares -= claimed_shares
    assert position.shares >= 0
    await position.save()

    active_events = get_active_events(claim_liquidity.storage)
    remainders = Decimal(0)
    for event_id in active_events:
        pool_event = await models.PoolEvent.filter(id=event_id).get()
        user = await position.user.get()
        claim, _ = await models.Claim.get_or_create(
            event=pool_event,
            position=position,
            defaults={
                'shares': 0,
                'user': user,
                'withdrawn': False
            }
        )

        claim.shares += claimed_shares
        await claim.save()

        pool_event.locked_shares += claimed_shares
        # All positive remainders are calculated in favor of Pool:
        remainder = claimed_shares * pool_event.provided % pool_event.total_shares
        remainders += from_mutez(1) if remainder > Decimal(0) else Decimal(0)
        await pool_event.save()

    pool_address = claim_liquidity.data.target_address
    pool, _ = await models.Pool.get_or_create(address=pool_address)
    pool.total_liquidity -= claimed_shares * pool.total_liquidity / pool.total_shares
    pool.total_liquidity += remainders
    assert pool.total_liquidity >= 0
    pool.total_shares -= claimed_shares
    assert pool.total_shares >= 0
    await pool.save()


from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.claim_liquidity import ClaimLiquidityParameter
from juster.types.pool.storage import PoolStorage
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
    for event_id in active_events:
        pool_event = await models.PoolEvent.filter(id=event_id).get()
        user = await position.user.get()
        claim = await models.Claim(
            event=pool_event,
            position=position,
            shares=claimed_shares,
            user=user,
            withdrawn=False,
        )
        await claim.save()

        pool_event.locked_shares += claimed_shares
        await pool_event.save()

    pool_address = claim_liquidity.data.target_address
    pool, _ = await models.Pool.get_or_create(address=pool_address)
    pool.total_liquidity -= claimed_shares * pool.total_liquidity / pool.total_shares
    assert pool.total_liquidity >= 0
    pool.total_shares -= claimed_shares
    assert pool.total_shares >= 0
    await pool.save()

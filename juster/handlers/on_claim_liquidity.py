
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from dipdup.models import Transaction
from juster.types.pool.parameter.claim_liquidity import ClaimLiquidityParameter

import juster.models as models
from juster.utils import (
    get_position,
    get_entry,
    process_pool_shares
)


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


from decimal import Decimal

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.new_event import NewEventParameter
from juster.types.juster.parameter.provide_liquidity import ProvideLiquidityParameter
from juster.types.juster.storage import JusterStorage
from juster.types.pool.parameter.create_event import CreateEventParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import from_mutez
from juster.utils import get_event
from juster.utils import get_pool_event
from juster.utils import process_pool_shares


async def on_create_event(
    ctx: HandlerContext,
    create_event: Transaction[CreateEventParameter, PoolStorage],
    new_event: Transaction[NewEventParameter, JusterStorage],
    provide_liquidity: Transaction[ProvideLiquidityParameter, JusterStorage],
) -> None:
    event_id, event_diff = get_event(new_event.storage)
    amount = from_mutez(provide_liquidity.data.amount)
    fees = from_mutez(new_event.data.amount)

    pool_event_id, pool_event_diff = get_pool_event(create_event.storage)
    assert pool_event_id == event_id
    total_shares = process_pool_shares(create_event.storage.totalShares)

    pool_address = create_event.data.target_address
    pool, _ = await models.Pool.get_or_create(address=pool_address)

    calculated_shares = (amount+fees) * pool.total_shares / pool.total_liquidity
    event_shares = process_pool_shares(pool_event_diff.shares)

    # allowing 1 mutez difference:
    assert abs(calculated_shares - event_shares) <= Decimal('0.000001')

    locked_shares = process_pool_shares(pool_event_diff.lockedShares)
    assert locked_shares == 0

    pool_event = models.PoolEvent(
        id=event_id,
        provided=amount + fees,
        result=None,
        shares=event_shares,
        total_shares=total_shares,
        locked_shares=locked_shares
    )
    await pool_event.save()

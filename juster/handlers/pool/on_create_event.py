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
    assert provide_liquidity.data.amount
    amount = from_mutez(provide_liquidity.data.amount)
    assert new_event.data.amount
    fees = from_mutez(new_event.data.amount)

    pool_event_id, pool_event_diff = get_pool_event(create_event.storage)
    assert pool_event_id == event_id, 'wrong updated event_id in diff'

    claimed = process_pool_shares(pool_event_diff.claimed)
    assert claimed == 0, 'wrong state: event created with claimed amount'

    pool_address = create_event.data.target_address
    pool = await models.Pool.get(address=pool_address)
    provided_amount = amount + fees
    pool.active_liquidity += provided_amount
    await pool.save()

    line_id = int(create_event.parameter.__root__)
    line = await models.PoolLine.get(line_id=line_id, pool=pool)

    pool_event = models.PoolEvent(
        id=event_id,
        provided=provided_amount,
        result=None,
        claimed=Decimal(0),
        pool=pool,
        line=line,
    )
    await pool_event.save()

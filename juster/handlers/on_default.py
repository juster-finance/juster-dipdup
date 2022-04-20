
from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.default import DefaultParameter
from juster.utils import from_mutez


async def on_default(
    ctx: HandlerContext,
    default: Transaction[DefaultParameter, PoolStorage],
) -> None:
    pool_address = default.data.target_address
    amount = from_mutez(default.data.amount)

    pool, _ = await models.Pool.get_or_create(address=pool_address)
    pool.total_liquidity += amount
    await pool.save()


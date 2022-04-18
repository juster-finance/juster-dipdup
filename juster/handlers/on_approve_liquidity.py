
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.approve_liquidity import ApproveLiquidityParameter
from dipdup.models import Transaction

from decimal import Decimal
from typing import Tuple
from typing import Union
import juster.models as models
from juster.types.pool.storage import Positions
from juster.types.pool.storage import PoolStorage


def get_position(storage: PoolStorage) -> Tuple[int, Positions]:
    assert len(storage.positions) == 1
    position_id = int(next(iter(storage.positions)))
    position_diff = storage.positions[str(position_id)]
    return position_id, position_diff


def process_pool_shares(raw: Union[str, int]) -> Decimal:
    return Decimal(raw) / (10**models.pool_share_precision)


async def on_approve_liquidity(
    ctx: HandlerContext,
    approve_liquidity: Transaction[ApproveLiquidityParameter, PoolStorage],
) -> None:

    position_id, position_diff = get_position(approve_liquidity.storage)
    sender = approve_liquidity.data.sender_address
    user, _ = await models.User.get_or_create(address=sender)
    shares = process_pool_shares(position_diff.shares)
    assert shares > 0

    position = models.PoolPosition(
        id=position_id,
        user=user,
        shares=shares,
    )
    await position.save()


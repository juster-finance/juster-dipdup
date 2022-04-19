
from dipdup.context import HandlerContext
from juster.types.pool.storage import PoolStorage
from juster.types.pool.parameter.withdraw_liquidity import WithdrawLiquidityParameter
from dipdup.models import Transaction

import juster.models as models


async def on_withdraw_liquidity(
    ctx: HandlerContext,
    withdraw_liquidity: Transaction[WithdrawLiquidityParameter, PoolStorage],
) -> None:
    # TODO: is it OK to access this __root__ or there are any other ways? [4]
    claims = withdraw_liquidity.parameter.__root__
    for claim_key in claims:
        event = await models.PoolEvent.filter(id=int(claim_key.eventId)).get()
        position = await models.PoolPosition.filter(id=int(claim_key.positionId)).get()
        claim = await models.Claim.filter(event=event, position=position).get()
        claim.withdrawn = True
        await claim.save()


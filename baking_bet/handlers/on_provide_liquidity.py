from dipdup.models import OperationHandlerContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.provide_liquidity import ProvideLiquidityParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import get_event, from_mutez


async def on_provide_liquidity(
    ctx: OperationHandlerContext,
    provide_liquidity: TransactionContext[ProvideLiquidityParameter, BetsStorage],
) -> None:
    event_id, event_diff = get_event(provide_liquidity.storage)
    amount = from_mutez(provide_liquidity.data.amount)

    event = await models.Event.filter(id=event_id).get()
    event.totalLiquidityShares = from_mutez(event_diff.totalLiquidityShares)  # type: ignore
    event.poolFor = from_mutez(event_diff.poolFor)  # type: ignore
    event.poolAgainst = from_mutez(event_diff.poolAgainst)  # type: ignore
    event.totalLiquidityProvided += amount
    await event.save()

    user, _ = await models.User.get_or_create(address=provide_liquidity.data.sender_address)
    user.totalLiquidityProvided += amount  # type: ignore
    await user.save()

    position, _ = await models.Position.get_or_create(
        event=event,
        user=user,
    )
    await position.save()

    shares = from_mutez(provide_liquidity.storage.liquidityShares[0].value)
    await models.Deposit(
        event=event,
        user=user,
        amount=amount,
        shares=shares
    ).save()

    # TODO: update all positions with shares (reward for/against based on total shares/provided)

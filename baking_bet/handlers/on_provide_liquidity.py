from decimal import Decimal
from typing import Optional

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import baking_bet.models as models
from baking_bet.types.bets.parameter.provide_liquidity import ProvideLiquidityParameter
from baking_bet.types.bets.storage import BetsStorage
from baking_bet.utils import from_mutez
from baking_bet.utils import from_mutez

from dipdup.models import OperationData, OperationHandlerContext, OriginationContext, TransactionContext

import baking_bet.models as models

from baking_bet.types.bets.parameter.provide_liquidity import ProvideLiquidityParameter
from baking_bet.types.bets.storage import BetsStorage


async def on_provide_liquidity(
    ctx: OperationHandlerContext,
    provide_liquidity: TransactionContext[ProvideLiquidityParameter, BetsStorage],
) -> None:
    updated_event = provide_liquidity.storage.events[0].value
    event_id = provide_liquidity.storage.events[0].key
    event = await models.Event.filter(id=event_id).get()
    event.betsAgainstLiquidityPoolSum = from_mutez(updated_event.betsAgainstLiquidityPoolSum)  # type: ignore
    event.betsForLiquidityPoolSum = from_mutez(updated_event.betsForLiquidityPoolSum)  # type: ignore
    event.firstProviderAgainstSharesSum = from_mutez(updated_event.firstProviderAgainstSharesSum)  # type: ignore
    event.firstProviderForSharesSum = from_mutez(updated_event.firstProviderForSharesSum)  # type: ignore
    event.totalLiquidityAgainstSharesSum = from_mutez(updated_event.totalLiquidityAgainstSharesSum)  # type: ignore
    event.totalLiquidityForSharesSum = from_mutez(updated_event.totalLiquidityForSharesSum)  # type: ignore
    event.totalLiquidityProvided = from_mutez(updated_event.totalLiquidityProvided)  # type: ignore
    await event.save()

    address = provide_liquidity.storage.providedLiquidityLedger[0].key.address
    user, _ = await models.User.get_or_create(address=address)
    await models.Ledger.update_or_create(
        event=event,
        user=user,
        defaults=dict(
            liquidityAgainstSharesLedger=from_mutez(provide_liquidity.storage.liquidityAgainstSharesLedger[0].value),
            liquidityForSharesLedger=from_mutez(provide_liquidity.storage.liquidityForSharesLedger[0].value),
            providedLiquidityLedger=from_mutez(provide_liquidity.storage.providedLiquidityLedger[0].value),
            winAgainstProfitLossPerShareAtEntry=models.to_share(provide_liquidity.storage.winAgainstProfitLossPerShareAtEntry[0].value),
            winForProfitLossPerShareAtEntry=models.to_share(provide_liquidity.storage.winForProfitLossPerShareAtEntry[0].value),
        ),
    )
    user.totalLiquidityProvided += from_mutez(provide_liquidity.storage.providedLiquidityLedger[0].value)  # type: ignore
    await user.save()

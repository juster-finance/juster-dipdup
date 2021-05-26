from typing import List

from dipdup.models import BigMapHandlerContext, BigMapContext

import baking_bet.models as models

from baking_bet.types.normalizer.big_map.asset_map_key import AssetMapKey
from baking_bet.types.normalizer.big_map.asset_map_value import AssetMapValue


async def on_oracle_update(
    ctx: BigMapHandlerContext,
    asset_map: List[BigMapContext[AssetMapKey, AssetMapValue]],
) -> None:
    for asset in asset_map:
        if not asset.value:
            continue
        symbol = asset.key.__root__
        currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=symbol)
        quote = models.Quote(
            currency_pair=currency_pair,
            price=asset.value.computedPrice,
            timestamp=asset.value.lastUpdateTime,
        )
        await quote.save()

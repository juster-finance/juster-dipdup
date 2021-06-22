from dipdup.models import BigMapDiff
from dipdup.context import HandlerContext
from typing import List


import juster.models as models

from juster.types.harbinger_normalizer.big_map.asset_map_key import AssetMapKey
from juster.types.harbinger_normalizer.big_map.asset_map_value import AssetMapValue


async def on_oracle_update(
    ctx: HandlerContext,
    asset_map: List[BigMapDiff[AssetMapKey, AssetMapValue]],
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

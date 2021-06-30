from dipdup.models import BigMapDiff
from dipdup.context import HandlerContext
from typing import List


import juster.models as models

from juster.types.harbinger_normalizer.big_map.asset_map_key import AssetMapKey
from juster.types.harbinger_normalizer.big_map.asset_map_value import AssetMapValue


async def on_oracle_update(
    ctx: HandlerContext,
    asset_map: BigMapDiff[AssetMapKey, AssetMapValue],
) -> None:
    if not asset_map.value:
        return
    symbol = asset_map.key.__root__
    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=symbol)
    quote = models.Quote(
        currency_pair=currency_pair,
        price=asset_map.value.computedPrice,
        timestamp=asset_map.value.lastUpdateTime,
        source=models.QuoteSource.HARBINGER,
    )
    await quote.save()

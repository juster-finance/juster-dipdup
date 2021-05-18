from typing import List

from dipdup.models import BigMapContext, BigMapHandlerContext

import baking_bet.models as models
from baking_bet.types.normalizer.big_map.asset_map_key import AssetMapKey
from baking_bet.types.normalizer.big_map.asset_map_value import AssetMapValue
import baking_bet.models as models
from baking_bet.types.normalizer.big_map.asset_map_key import AssetMapKey
from baking_bet.types.normalizer.big_map.asset_map_value import AssetMapValue
from dipdup.models import BigMapContext, BigMapHandlerContext


async def on_oracle_update(
    ctx: BigMapHandlerContext,
    asset_map: List[BigMapContext[AssetMapKey, AssetMapValue]],
) -> None:
    for asset in asset_map:
        if not asset.value:
            continue
        symbol, _ = await models.Symbol.get_or_create(symbol=asset.key.__root__)
        price = models.Quote(
            symbol=symbol,
            price=asset.value.computedPrice,
            timestamp=asset.value.lastUpdateTime,
        )
        await price.save()

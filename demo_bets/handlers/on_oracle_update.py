from typing import List

import demo_bets.models as models
from demo_bets.types.normalizer.big_map.asset_map_key import AssetMapKey
from demo_bets.types.normalizer.big_map.asset_map_value import AssetMapValue
from dipdup.models import BigMapContext, BigMapHandlerContext


async def on_oracle_update(
    ctx: BigMapHandlerContext,
    asset_map: List[BigMapContext[AssetMapKey, AssetMapValue]],
) -> None:
    for asset in asset_map:
        if not asset.value:
            continue
        price = models.Quote(
            symbol=asset.key.__root__,
            price=asset.value.computedPrice,
            timestamp=asset.value.lastUpdateTime,
        )
        await price.save()

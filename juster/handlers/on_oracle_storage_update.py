from dipdup.context import HandlerContext
from dipdup.models import BigMapDiff

import juster.models as models
from juster.types.harbinger_storage.big_map.oracle_data_key import OracleDataKey
from juster.types.harbinger_storage.big_map.oracle_data_value import OracleDataValue


async def on_oracle_storage_update(
    ctx: HandlerContext,
    oracle_data: BigMapDiff[OracleDataKey, OracleDataValue],
) -> None:
    if not oracle_data.value:
        return
    assert oracle_data.key
    symbol = oracle_data.key.__root__
    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=symbol)
    quote = models.Quote(
        currency_pair=currency_pair,
        price=oracle_data.value.nat_3,
        timestamp=oracle_data.value.timestamp_1,
        source=models.QuoteSource.HARBINGER_RAW,
    )
    await quote.save()

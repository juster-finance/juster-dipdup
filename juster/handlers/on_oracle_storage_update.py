from dipdup.context import HandlerContext
from dipdup.models import BigMapDiff
from datetime import datetime

import juster.models as models
from juster.types.harbinger_storage.big_map.oracle_data_key import OracleDataKey
from juster.types.harbinger_storage.big_map.oracle_data_value import OracleDataValue


async def on_oracle_storage_update(
    ctx: HandlerContext,
    oracle_data: BigMapDiff[OracleDataKey, OracleDataValue],
) -> None:
    if not oracle_data.action.has_value:
        return
    assert oracle_data.key
    assert oracle_data.value
    if not int(oracle_data.value.nat_0):
        return

    symbol = oracle_data.key.__root__
    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=symbol)

    await models.Candle.update_or_create(
        id=models.candle_pk(models.Source.HARBINGER,
                            currency_pair.id,
                            datetime.fromisoformat(oracle_data.value.timestamp_1[:-1])),
        defaults=dict(
            currency_pair=currency_pair,
            source=models.Source.HARBINGER,
            since=oracle_data.value.timestamp_0,
            until=oracle_data.value.timestamp_1,
            interval=models.CandleInterval.ONE_MINUTE,
            open=models.to_decimal(oracle_data.value.nat_0),
            high=models.to_decimal(oracle_data.value.nat_1),
            low=models.to_decimal(oracle_data.value.nat_2),
            close=models.to_decimal(oracle_data.value.nat_3),
            volume=models.to_decimal(oracle_data.value.nat_4)
        )
    )

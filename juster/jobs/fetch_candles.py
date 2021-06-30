import asyncio
from typing import Any, Dict, cast
from dipdup.datasources.coinbase.models import CandleInterval
from dipdup.datasources.coinbase.datasource import CoinbaseDatasource
from datetime import datetime, timedelta, timezone
from dipdup.context import DipDupContext
from juster import models


async def fetch_candles(ctx: DipDupContext, args: Dict[str, Any]) -> None:
    await asyncio.sleep(5)
    datasource = cast(CoinbaseDatasource, ctx.datasources[args['datasource']])
    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=args['currency_pair'])
    candle_interval = CandleInterval[args['candle_interval']]
    since = datetime.fromisoformat(args['since'])

    last_candle = await models.Candle.filter(currency_pair=currency_pair, interval=candle_interval).order_by('-timestamp').first()
    request_since = last_candle.timestamp + timedelta(seconds=1) if last_candle else since
    request_until = datetime.utcnow().replace(tzinfo=timezone.utc)
    candles = await datasource.get_candles(
        since=request_since,
        until=request_until,
        interval=candle_interval,
        ticker=currency_pair.symbol,
    )
    for candle in candles:
        await models.Candle(
            currency_pair=currency_pair,
            timestamp=candle.timestamp,
            interval=candle_interval,
            open=candle.open,
            close=candle.close,
            high=candle.high,
            low=candle.low,
            volume=candle.volume,
        ).save()

import logging
from typing import Any, Dict, cast
from datetime import datetime, timedelta, timezone
from dipdup.datasources.coinbase.models import CandleInterval
from dipdup.datasources.coinbase.datasource import CoinbaseDatasource
from dipdup.context import DipDupContext

from juster import models


async def fetch_coinbase_candles(ctx: DipDupContext, args: Dict[str, Any]) -> None:
    logger = logging.getLogger('fetch_candles')
    datasource = cast(CoinbaseDatasource, ctx.datasources[args['datasource']])
    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=args['currency_pair'])
    candle_interval = CandleInterval[args['candle_interval']]
    since = datetime.fromisoformat(args['since']).replace(tzinfo=timezone.utc)
    logger.info('Fetching %s %s candles from coinbase', currency_pair.symbol, candle_interval.value)

    last_candle = await models.Candle.filter(
        currency_pair=currency_pair,
        interval=candle_interval,
        source=models.Source.COINBASE
    ).order_by('-until').first()
    request_since = last_candle.until + timedelta(seconds=1) if last_candle else since
    request_until = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=1)
    logger.info('Since %s until %s', request_since.isoformat(), request_until.isoformat())

    raw_candles = await datasource.get_candles(
        since=request_since,
        until=request_until,
        interval=candle_interval,
        ticker=currency_pair.symbol,
    )
    logger.info('%s %s %s candles fetched', len(raw_candles), currency_pair.symbol, candle_interval.value)

    for raw_candle in raw_candles:
        candle = models.Candle(
            currency_pair=currency_pair,
            since=raw_candle.timestamp - timedelta(seconds=candle_interval.seconds),
            until=raw_candle.timestamp,
            interval=candle_interval,
            open=raw_candle.open,
            close=raw_candle.close,
            high=raw_candle.high,
            low=raw_candle.low,
            volume=raw_candle.volume,
            source=models.Source.COINBASE,
        )
        await candle.save()

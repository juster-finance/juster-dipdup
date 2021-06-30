import asyncio
import logging
from sqlite3 import Timestamp
from typing import Any, Dict, cast
from dipdup.datasources.coinbase.models import CandleInterval
from dipdup.datasources.coinbase.datasource import CoinbaseDatasource
from datetime import datetime, timedelta, timezone
from dipdup.context import DipDupContext
from juster import models


async def fetch_candles(ctx: DipDupContext, args: Dict[str, Any]) -> None:
    logger = logging.getLogger('fetch_candles')
    datasource = cast(CoinbaseDatasource, ctx.datasources[args['datasource']])
    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=args['currency_pair'])
    candle_interval = CandleInterval[args['candle_interval']]
    since = datetime.fromisoformat(args['since']).replace(tzinfo=timezone.utc)
    points = int(args['points'])

    logger.info('Fetching %s %s candles', currency_pair, candle_interval.value)
    last_candle = await models.Candle.filter(currency_pair=currency_pair, interval=candle_interval).order_by('-timestamp').first()
    request_since = last_candle.timestamp + timedelta(seconds=1) if last_candle else since
    request_until = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=1)
    logger.info('Since %s until %s', request_since.isoformat(), request_until.isoformat())
    raw_candles = await datasource.get_candles(
        since=request_since,
        until=request_until,
        interval=candle_interval,
        ticker=currency_pair.symbol,
    )
    logger.info('%s candles fetched', len(raw_candles))
    candles = []
    for raw_candle in raw_candles:
        candle = models.Candle(
            currency_pair=currency_pair,
            timestamp=raw_candle.timestamp,
            interval=candle_interval,
            open=raw_candle.open,
            close=raw_candle.close,
            high=raw_candle.high,
            low=raw_candle.low,
            volume=raw_candle.volume,
        )
        await candle.save()
        candles.append(candle)

    logger.info('Calculating quotes normalized by %s points', points)
    if len(candles) < points:
        candles += (
            await models.Candle.filter(
                currency_pair=currency_pair,
                interval=candle_interval,
                timestamp__lt=candles[0].timestamp,
            )
            .order_by('-timestamp')
            .limit(points - len(candles))
            .all()
        )

    index = points
    while index < len(candles):
        candles_batch = candles[index - points : index]
        prices = [(c.high + c.low + c.close) / 3 * c.volume for c in candles_batch]
        volumes = [c.volume for c in candles_batch]
        await models.Quote(
            price=sum(prices) / sum(volumes) * 1000000,
            timestamp=candles_batch[-1].timestamp,
            currency_pair=currency_pair,
            source=models.QuoteSource.COINBASE,
        ).save()
        index += 1

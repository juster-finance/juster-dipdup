import logging
from datetime import datetime, timedelta, timezone
from typing import cast

from dipdup.context import HookContext
from dipdup.datasources.coinbase.datasource import CoinbaseDatasource
from dipdup.datasources.coinbase.models import CandleInterval

from juster import models


async def fetch_coinbase_candles(ctx: HookContext, datasource: str, candle_interval: str, since: str, currency_pair: str,) -> None:
    logger = logging.getLogger('fetch_candles')
    coinbase = cast(CoinbaseDatasource, ctx.datasources[datasource])
    currency_pair_model, _ = await models.CurrencyPair.get_or_create(symbol=currency_pair)
    candle_interval_enum = CandleInterval[candle_interval]
    since_datetime = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
    logger.info('Fetching %s %s candles from coinbase', currency_pair_model.symbol, candle_interval_enum.value)

    last_candle = (
        await models.Candle.filter(
            currency_pair=currency_pair_model,
            interval=candle_interval_enum,
            source=models.Source.COINBASE,
        )
        .order_by('-until')
        .first()
    )
    batch_since = last_candle.until + timedelta(seconds=1) if last_candle else since_datetime
    request_until = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=1)
    if candle_interval_enum != CandleInterval.ONE_MINUTE:
        raise NotImplementedError
    interval = timedelta(hours=6)
    batch_until = batch_since + interval

    while batch_until < request_until + interval:
        logger.info('Since %s until %s', batch_since.isoformat(),batch_until.isoformat())

        raw_candles = await coinbase.get_candles(
            since=batch_since,
            until=batch_until,
            interval=candle_interval_enum,
            ticker=currency_pair_model.symbol,
        )
        logger.info('%s %s %s candles fetched', len(raw_candles), currency_pair_model.symbol, candle_interval_enum.value)

        for raw_candle in raw_candles:
            candle = models.Candle(
                currency_pair=currency_pair_model,
                since=raw_candle.timestamp - timedelta(seconds=candle_interval_enum.seconds),
                until=raw_candle.timestamp,
                interval=candle_interval_enum,
                open=raw_candle.open,
                close=raw_candle.close,
                high=raw_candle.high,
                low=raw_candle.low,
                volume=raw_candle.volume,
                source=models.Source.COINBASE,
            )
            await candle.save()

        batch_since += interval
        batch_until += interval

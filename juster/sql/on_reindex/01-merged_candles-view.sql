CREATE MATERIALIZED VIEW merged_candles AS
SELECT
    coalesce(hb.currency_pair_id, cb.currency_pair_id) AS currency_pair_id,
    coalesce(hb.source, cb.source) AS source,
    coalesce(hb.until, cb.until) AS until,
    coalesce(hb.open, cb.open) AS open,
    coalesce(hb.high, cb.high) AS high,
    coalesce(hb.low, cb.low) AS low,
    coalesce(hb.close, cb.close) AS close,
    coalesce(hb.volume, cb.volume) AS volume
FROM
    (SELECT * FROM candle WHERE source = 'HARBINGER') hb
    FULL OUTER JOIN (SELECT * FROM candle WHERE source = 'COINBASE') cb
    ON hb.until = cb.until and hb.currency_pair_id = cb.currency_pair_id;
-- sorted in the window function
-- ORDER BY until;
CREATE UNIQUE INDEX merged_candles_id ON merged_candles (currency_pair_id, source, until);
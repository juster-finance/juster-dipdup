CREATE OR REPLACE VIEW merged_candles AS
SELECT
  DISTINCT ON (mc.until) *
FROM
  (
    SELECT
      COALESCE(c1.id, c2.id) as id,
      COALESCE(c1.source, c2.source) as source,
      COALESCE(c1.until, c2.until) as until,
      COALESCE(c1.open, c2.open) as open,
      COALESCE(c1.high, c2.high) as high,
      COALESCE(c1.low, c2.low) as low,
      COALESCE(c1.close, c2.close) as close,
      COALESCE(c1.volume, c2.volume) as volume
    FROM
      juster.candle c1 FULL
      OUTER JOIN juster.candle c2 ON c1.until = c2.until
    WHERE
      COALESCE(c1.currency_pair_id, c2.currency_pair_id) = 1
    ORDER BY
      until DESC
  ) mc;
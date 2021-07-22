CREATE VIEW quotes_wma AS
SELECT
  mc.until AS timestamp,
  SUM(
    (mc7.high + mc7.low + mc7.close) / 3 * mc7.volume
  ) / SUM(mc7.volume) as price
FROM
  merged_candles mc
  JOIN merged_candles mc7 ON mc7.until <= mc.until
  AND mc7.until >= mc.until - '7 days' :: INTERVAL
GROUP BY
  mc.until
ORDER BY
  mc.until DESC;
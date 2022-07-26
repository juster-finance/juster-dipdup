CREATE MATERIALIZED VIEW quotes_wma AS
SELECT
    x.timestamp,
    x.currency_pair_id,
    x.weighted_price / x.total_volume AS price
FROM (
	SELECT
		mc.until AS timestamp,
		mc.currency_pair_id AS currency_pair_id,
		sum((mc.close + mc.high + mc.low) * mc.volume / 3) OVER seven AS weighted_price,
		sum(mc.volume) OVER seven AS total_volume
	FROM merged_candles mc
	WINDOW seven AS (
	    partition by mc.currency_pair_id
	    ORDER BY mc.until
	    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
	)
) AS x
ORDER BY x.timestamp;
CREATE UNIQUE INDEX quotes_wma_id ON quotes_wma (currency_pair_id, timestamp);

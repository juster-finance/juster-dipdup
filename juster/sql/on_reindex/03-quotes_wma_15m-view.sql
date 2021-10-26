CREATE OR REPLACE VIEW quotes_wma_15m AS
SELECT
    qw.timestamp,
    qw.currency_pair_id,
    qw.price
FROM juster.quotes_wma qw
where mod(extract(epoch FROM qw.timestamp)::int4, 900) = 0
ORDER BY qw.timestamp
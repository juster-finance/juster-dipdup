create or replace view quotes_wma_15m as
select
    qw.timestamp,
    qw.currency_pair_id,
    qw.price
from juster.quotes_wma qw
where mod(extract(epoch from qw.timestamp)::int4, 900) = 0
order by qw.timestamp
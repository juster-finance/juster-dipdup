create or replace view merged_candles as
select
    coalesce(hb.currency_pair_id, cb.currency_pair_id) as currency_pair_id,
    coalesce(hb.source, cb.source) as source,
    coalesce(hb.until, cb.until) as until,
    coalesce(hb.open, cb.open) as open,
    coalesce(hb.high, cb.high) as high,
    coalesce(hb.low, cb.low) as low,
    coalesce(hb.close, cb.close) as close,
    coalesce(hb.volume, cb.volume) as volume
from
    (select * from juster.candle WHERE source = 'HARBINGER') hb
    full outer join (select * from juster.candle WHERE source = 'COINBASE') cb
    on hb.until = cb.until and hb.currency_pair_id = cb.currency_pair_id
order by until
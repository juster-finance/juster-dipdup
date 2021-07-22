create or replace view quotes_wma as
select
    x.timestamp,
    x.currency_pair_id,
    x.weighted_price / x.total_volume as price
from (
	select
		mc.until as timestamp,
		mc.currency_pair_id as currency_pair_id,
		sum((mc.close + mc.high + mc.low) * mc.volume / 3) over seven as weighted_price,
		sum(mc.volume) over seven as total_volume
	from juster.merged_candles mc
	window seven as (
	    partition by mc.currency_pair_id
	    order by mc.until
	    rows between 6 preceding and current row
	)
) as x
order by x.timestamp
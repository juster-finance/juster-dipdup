create or replace view total_value_locked as
select
	x.event_id,
	x.created_time,
	x.amount,
	sum(x.amount) over (
	  partition by x.event_id
	  order by x.created_time
	) as cum_sum
from (
	select c.event_id, c.created_time, sum(c.amount) as amount
	from (
		select b.event_id, b.created_time, b.amount
		from bet b
		union select d.event_id, d.created_time, (d.amount_above_eq + d.amount_below) as amount
		from deposit d
	) as c
	group by c.event_id, c.created_time
) as x
order by x.event_id, x.created_time;
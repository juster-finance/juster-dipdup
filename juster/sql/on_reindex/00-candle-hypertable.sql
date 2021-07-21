ALTER TABLE juster.candle DROP CONSTRAINT candle_pkey;
ALTER TABLE juster.candle ADD PRIMARY KEY (id, until);
SELECT public.create_hypertable('juster.candle', 'until');

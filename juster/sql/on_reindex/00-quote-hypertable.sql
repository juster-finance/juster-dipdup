ALTER TABLE juster.quote DROP CONSTRAINT quote_pkey;
ALTER TABLE juster.quote ADD PRIMARY KEY (id, timestamp);
SELECT public.create_hypertable('juster.quote', 'timestamp');

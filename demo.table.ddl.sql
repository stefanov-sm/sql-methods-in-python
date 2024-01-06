create table tests.the_table
(
  seq integer primary key not null,
  ts timestamp default '2023-12-01'::date + '00:00:01'::interval * (random()*3600*24) not null,
  value text default replace(gen_random_uuid()::text, '-', '') not null,
  status integer default (random() * 97)::integer % 11 not null
);

insert into tests.the_table (seq) 
select generate_series(1, 100000, 1);

drop table if exists tests.hardtest;

create table tests.hardtest
(
 subject text,
 xname text,
 xdatetime timestamp,
 currency_iso text,
 xrate numeric
); 

-- check
select * from tests.hardtest;
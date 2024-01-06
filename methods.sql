-- Demo queries

--! {"name": "named_recordset", "param_mode": "named", "returns":"recordset"}
select seq, ts::text, value
from tests.the_table
where seq between :seq_from and :seq_to
  and status = :status
order by seq
limit 5;

--! {"name": "positional_record", "param_mode": "positional", "returns":"record"}
select ts::text, value, status
from tests.the_table
where seq = ?;

--! {"name": "named_value", "param_mode": "named", "returns":"value"}
select value
from tests.the_table
where seq = :seq;

--! {"name": "positional_none", "param_mode": "positional", "returns":"none"}
insert into tests.the_table (seq, status)
values (?, ?);

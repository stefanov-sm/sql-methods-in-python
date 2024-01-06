-- More demo queries

--! {"name": "Roman_64_numerals", "param_mode":"positional", "returns": "recordset"}
select n, to_char(n + 64, 'FMRN') rn
from generate_series(1, ?, 1) as t(n);

--! {"name": "cleanup", "param_mode":"named", "returns": "none"}
delete from tests.the_table
where seq = :seq;

--! {"name": "commit", "param_mode":"none", "returns": "none"}
commit;

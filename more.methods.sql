-- More demo queries

--! {"name": "Roman_64_numerals", "param_mode":"positional", "returns": "recordset"}
select n, to_char(n + 64, 'FMRN') rn
from generate_series(1, ?, 1) as t(n);

--! {"name": "cleanup", "param_mode":"named", "returns": "value"}
with t(n) as
(
 delete from tests.the_table
 where seq >= :seq
 returning 1
)
select count(n) from t;

--! {"name": "commit", "param_mode":"none", "returns": "none"}
commit;

--! {"name": "rollback", "param_mode":"none", "returns": "none"}
rollback;

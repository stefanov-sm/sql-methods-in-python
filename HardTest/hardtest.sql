--! {"name":"hardtest_marshalling", "param_mode":"positional", "returns":"value"}
with t as
(
  insert into tests.hardtest
   with t as
   (
    select *,
    (rn - 1) %% 5 col_no,
    (rn - 1) / 5 row_no
    from tests.spreadsheetml_table(?::xml)
   )
   select
     max(cell_data) filter (where col_no = 0) subject,
     max(cell_data) filter (where col_no = 1) "name",
     max(cell_data) filter (where col_no = 2) ::timestamp date_time,
     max(cell_data) filter (where col_no = 3) "ISO (currency)",
     max(cell_data) filter (where col_no = 4) ::numeric rate
   from t
   where row_no > 0
   group by row_no
   order by row_no 
  returning 1
)
select count(*) from t;

--! {"name":"hardtest_fileaccess", "param_mode":"positional", "returns":"value"}
with t as
(
  insert into tests.hardtest
   with t as
   (
    select *,
    (rn - 1) %% 5 col_no,
    (rn - 1) / 5 row_no
    from tests.spreadsheetml_fromfile(?)
   )
   select
     max(cell_data) filter (where col_no = 0) subject,
     max(cell_data) filter (where col_no = 1) "name",
     max(cell_data) filter (where col_no = 2) ::timestamp date_time,
     max(cell_data) filter (where col_no = 3) "ISO (currency)",
     max(cell_data) filter (where col_no = 4) ::numeric rate
   from t
   where row_no > 0
   group by row_no
   order by row_no 
  returning 1
)
select count(*) from t;

--! {"name":"hardtest_count", "param_mode":"none", "returns":"value"}
select count(*) from tests.hardtest;
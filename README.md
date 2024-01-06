# sql-methods-in-python
### Define Python methods as SQL queries

Implements DB-API 2.0 parameter styles `qmark` (like `where name = ?`) and `named` (like `where name = :name`).  
Uses psycopg3 database driver and PostgreSQL. Can be ported to use any DB-API 2.0 database driver.

SQL method specifiers are lines that start with `--!` folowed by JSON with exactly these mandatory attributes:
1. `"name"` - specifies the method name as a valid identifier, K&R style;
2. `"returns"` - specifies the method return type. Can be one of:
   * `"value"` - a scalar;
   * `"record"` - a dictionary representing a single record;
   * `"recordset"` - a list of dictionaries;  
   * `"none"`
3. `"param_mode"` - specifies the SQL parameter style. Can be one of:
   * `"named"` - as in `where name = :name`;
   * `"positional"` - `qmark` style, as in `where name = ?`;
   * `"none"`  

Example: `--! {"name": "Roman_64_numerals", "param_mode":"positional", "returns": "recordset"}`

Queries can be of any length and complexity. Comments, empty lines and leading/trailing whitespaces in SQL files are ignored.  

> [!IMPORTANT]
> SQL files must be UTF-8 encoded.

```python
import json
import psycopg
import demo_settings as cfg
import dbgw

with psycopg.connect(cfg.CONNECTIONSTRING) as conn:
  db = dbgw.db_gateway(
                       conn,
                       cfg.SQLPATH + 'methods.sql',
                       cfg.SQLPATH + 'more.methods.sql',
                       autocommit = False
                      )
  res = db.named_recordset({'seq_from': 1000, 'seq_to': 1099, 'status': 5})
  print ('\r\nnamed_recordset:', json.dumps(res, indent = 2))
  res = db.positional_record(12345)
  print ('\r\npositional_record:', json.dumps(res, indent = 2))
  res = db.named_value({'seq':54321})
  print ('\r\nnamed_value:', res)
  res = db.positional_none(13, 123)
  db.commit()
  print ('\r\npositional_none:', res)
  res = db.Roman_64_numerals(10)
  print ('\r\nRoman_64_numerals:', json.dumps(res, indent = 2))
  res = db.cleanup({'seq':200000});
  db.commit()
  print ('\r\ncleanup:', res)

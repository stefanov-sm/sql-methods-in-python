# sql-methods-in-python
### Define Python methods as SQL queries

Uses **Psycopg 3** database driver and PostgreSQL. Can be ported to use another DB-API 2.0 compliant database driver.  
Implements [parameter styles](https://peps.python.org/pep-0249/#paramstyle) `qmark` (like `where name = ?`) and `named` (like `where name = :name`).  

#### Methods definition
Methods are defined in SQL files (see *methods.sql*) that consist of one or more sections like this:
```
sql method specifier line
line(s) of SQL code
```
A SQL method specifier line start with `--!` folowed by JSON with exactly these attributes:
1. **name** - specifies the method name as a valid identifier, K&R style;
2. **returns** - specifies the method return type. Can be one of:
   * **value** - returns a scalar;
   * **record** - returns a dictionary representing a single record;
   * **recordset** - returns a list of dictionaries;  
   * **none** - returns `None`
3. **param_mode** - specifies the SQL parameter style. Can be one of:
   * **named** - `named` style, as in `where name = :name`;
   * **positional** - `qmark` style, as in `where name = ?`;
   * **none** - no parameters  

Example:

    --! {"name": "Roman_64_numerals", "param_mode": "positional", "returns": "recordset"}

Queries can be of any length and complexity. Comments, empty lines and leading/trailing whitespaces in SQL files are ignored.  

> [!IMPORTANT]
> SQL files must be UTF-8 encoded.  

#### Gateway constructor signature
    db_gateway(connection, *sql_files, **autocommit_mode)  
where `autocommit_mode` (optional) can be `autocommit = True` (the default) or `autocommit = False`  
  
#### Usage example
Usage illustration and details in demo files (*demo.py*, *methods.sql* and *more.methods.sql*)
```python
import json
import psycopg
import dbgw
with psycopg.connect(<CONNECTIONSTRING>) as conn:
  db = dbgw.db_gateway(
                       conn,
                       <PATH-TO-SQLFILES> + 'methods.sql', <PATH-TO-SQLFILES> + 'more.methods.sql',
                       autocommit = False
                      )
  res = db.named_recordset({'seq_from':1000, 'seq_to':1099, 'status':5})
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

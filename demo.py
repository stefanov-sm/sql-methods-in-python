import json
import psycopg
from demo_settings import CONNECTIONSTRING, SQLPATH
from dbgw import db_gateway

NEWLINE = '\r\n'
with psycopg.connect(CONNECTIONSTRING) as conn:

  db = db_gateway(conn, SQLPATH + 'methods.sql', SQLPATH + 'more.methods.sql', autocommit = False)

  res = db.named_recordset({'seq_from': 1000, 'seq_to': 1099, 'status': 5})
  print (NEWLINE + 'named_recordset:', json.dumps(res, indent = 2))

  res = db.positional_record(12345)
  print (NEWLINE + 'positional_record:', json.dumps(res, indent = 2))

  res = db.named_value({'seq':54321})
  print (NEWLINE + 'named_value:', res)

  res = db.positional_none(13, 123)
  db.commit()
  print (NEWLINE + 'positional_none:', res)

  res = db.Roman_64_numerals(10)
  print (NEWLINE + 'Plus 64 Roman:')
  for rec in res: print(f">> {rec['n']}, {rec['rn']}")

  res = db.cleanup({'seq':200000})
  db.commit()
  print (NEWLINE + 'cleanup:', res)

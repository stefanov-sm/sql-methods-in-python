import datetime
import psycopg
import dbgw
import app_settings as cfg

DATAFILENAME = 'path-to/ecb.xml'
with psycopg.connect(cfg.CONNECTIONSTRING) as conn:

  db = dbgw.db_gateway(conn, cfg.SQLPATH + 'hardtest.sql', autocommit = True)

  start_time = datetime.datetime.now()
  with open(DATAFILENAME, 'r') as f:
    excel_linescount = db.hardtest_marshalling(f.read())
  print(f'Execution time of hardtest_marshalling: {datetime.datetime.now() - start_time}')
  print(f'Number of ETL-ed Excel lines: {excel_linescount}')

  start_time = datetime.datetime.now()
  excel_linescount = db.hardtest_fileaccess(DATAFILENAME)
  print(f'Execution time of hardtest_fileaccess: {datetime.datetime.now() - start_time}')
  print(f'Number of ETL-ed Excel lines: {excel_linescount}')
  
  print(f'\nTotal number of lines in the table: {db.hardtest_count()}')

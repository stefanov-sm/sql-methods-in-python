import re
import json
import psycopg
from psycopg.rows import dict_row, tuple_row

NAMED_RX = r'([^:])\B:([a-z_A-Z]\w+)\b'
NAMED_SUB = r'\1%(\2)s'
QMARK_RX = r'\B\?\B'

class db_gateway:
  def __init__(this, conn, *sqlfiles, **commit_mode):
    this.__conn = conn
    this.__method_wh = {}
    this.__autocommit = commit_mode['autocommit'] if 'autocommit' in commit_mode else True

    for sqlfile in sqlfiles: this.__import(sqlfile)

    # Rewrite named and qmark paramstyle (DB-API 2.0) queries to pyformat paramstyle
    for method_name in this.__method_wh:
      method_def = this.__method_wh[method_name]
      match method_def['param_mode']:
        case 'named': method_def['sql'] = re.sub(NAMED_RX, NAMED_SUB, method_def['sql'])
        case 'positional': method_def['sql'] = re.sub(QMARK_RX, '%s', method_def['sql'])

  def __method_factory(ignored, context):
    # Freeze (closure) context
    def sql_method(*args):
      method_def = context['method_def']  
      returns = method_def['returns']
      match method_def['param_mode']:
        case 'named': call_args = args[0]
        case 'positional': call_args = args
        case 'none': call_args = {}
      with context['conn'].cursor() as statement:
        statement.row_factory = tuple_row if returns in ('value', 'none') else dict_row
        statement.execute(method_def['sql'], call_args, prepare = True)
        if context['autocommit']: context['conn'].commit()
        match returns:
          case 'recordset': return statement.fetchall()
          case 'record': return statement.fetchone()
          case 'value': 
            rec = statement.fetchone()
            return None if rec is None else rec[0]
          case 'none': return None
    return sql_method

  def __import(this, sqlfile):
    method_name = None; line_nr = 0
    with open(sqlfile, 'r') as f:
      for rowline in f:
        line = rowline.strip()
        line_nr += 1
        if line[0:3] == '--!':

          method_json = None
          try: method_json = json.loads(line[3:])
          except: pass
          if (
              not method_json
              or len(method_json) != 3
              or not 'name' in method_json
              or not re.search(r'^[a-z_A-Z]\w+$', method_json['name'])
              or not 'returns' in method_json
              or not method_json['returns'] in ('recordset', 'record', 'value', 'none')
              or not 'param_mode' in method_json
              or not method_json['param_mode'] in ('named', 'positional', 'none')
             ):
            raise Exception (f'Invalid method specifier, file {sqlfile}, line {line_nr}')
        
          method_name = method_json['name']
          this.__method_wh[method_name] = {
            'sql':'',
            'returns':method_json['returns'],
            'param_mode':method_json['param_mode']
          }
          running_context = {
            'method_def':this.__method_wh[method_name],
            'conn':this.__conn,
            'autocommit':this.__autocommit
           }
        
          # Attached function, not a bound method
          setattr(this, method_name, this.__method_factory(running_context))
          continue
        
        if line == '' or line[0:2] == '--': continue
        if not method_name:
          raise Exception (f'Code found before a method is specified, file {sqlfile}, line {line_nr}')
        else:
          this.__method_wh[method_name]['sql'] += rowline

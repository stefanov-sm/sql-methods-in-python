import re
import json
import psycopg
from psycopg.rows import dict_row, tuple_row

class db_gateway:
    
    def __init__(this, conn, *sqlfiles, **commit_mode):
        this.__conn = conn
        this.__method_wh = {}
        this.__autocommit = commit_mode['autocommit'] if 'autocommit' in commit_mode else True

        for sqlfile in sqlfiles: this.__import(sqlfile)

        for method_name in this.__method_wh: # Rewrite named and qmark paramstyle (DB-API 2.0) queries to pyformat paramstyle
            method_def = this.__method_wh[method_name]
            match method_def['param_mode']:
                case 'named': method_def['sql'] = re.sub(r'([^:])\B:([a-z_A-Z]\w+)\b', r'\1%(\2)s', method_def['sql'])
                case 'positional': method_def['sql'] = re.sub(r'\B\?\B', '%s', method_def['sql'])

    def __method_factory(ignored, context):
        def sql_method(*args): # Freeze (closure) context
            method_def = context['method_def']
            match method_def['param_mode']:
                case 'named': call_args = args[0]
                case 'positional': call_args = args
                case 'none': call_args = {}
            with context['conn'].cursor() as statement:
                statement.row_factory = dict_row if method_def['returns'] in ('recordset', 'record') else tuple_row
                statement.execute(method_def['sql'], call_args, prepare = True)
                if context['autocommit']: context['conn'].commit()
                match method_def['returns']:
                    case 'recordset': return statement.fetchall()
                    case 'record': return statement.fetchone()
                    case 'value': return statement.fetchone()[0]
                    case 'none': return None
        return sql_method

    def __import(this, sqlfile):
        method_name = None
        f = open(sqlfile, 'r')
        linelist = f.readlines()
        f.close()

        for i in range(len(linelist)):
            line = linelist[i].strip()
            if line[0:3] == '--!':

                try: method_json = json.loads(line[3:])
                except: pass                   
                if (
                    not 'method_json' in locals() or len(method_json) != 3
                    or not 'name' in method_json or not re.search(r'^[a-z_A-Z]\w+$', method_json['name'])
                    or not 'returns' in method_json or not method_json['returns'] in ('recordset', 'record', 'value', 'none')
                    or not 'param_mode' in method_json or not method_json['param_mode'] in ('named', 'positional', 'none')
                   ):
                    raise Exception (f'Invalid method specifier, file {sqlfile}, line {i + 1}')

                method_name = method_json['name']
                this.__method_wh[method_name] = {'sql':'', 'returns':method_json['returns'], 'param_mode':method_json['param_mode']}
                running_context = {'method_def':this.__method_wh[method_name], 'conn':this.__conn, 'autocommit':this.__autocommit}
                setattr(this, method_name, this.__method_factory(running_context)) # Attached function, not a bound method

                continue

            if line == '' or line[0:2] == '--': continue
            if not method_name:
                raise Exception (f'Code found before a method is specified, file {sqlfile}, line {i + 1}')
            else:
                this.__method_wh[method_name]['sql'] += linelist[i]

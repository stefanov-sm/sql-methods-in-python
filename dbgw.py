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

        # rewrite named and qmark paramstyle (DB-API 2.0) queries to pyformat paramstyle
        for method_name in this.__method_wh:
            method_def = this.__method_wh[method_name]
            match method_def['param_mode']:
                case 'named': method_def['sql'] = re.sub(r'([^:])\B:([a-z_A-Z]\w+)\b', r'\1%(\2)s', method_def['sql'])
                case 'positional': method_def['sql'] = re.sub(r'\B\?\B', '%s', method_def['sql'])

    def __method_factory(this, method_name):
        # Freeze "method_name" of the current run context
        def sql_method(this, *args):
            ret_mode = this.__method_wh[method_name]['returns']
            match this.__method_wh[method_name]['param_mode']:
                case 'named': call_args = args[0]
                case 'positional': call_args = args
                case 'none': call_args = {}
            with this.__conn.cursor() as statement:
                statement.row_factory = dict_row if ret_mode in ('recordset', 'record') else tuple_row
                statement.execute(this.__method_wh[method_name]['sql'], call_args, prepare = True)
                if this.__autocommit: this.__conn.commit()
                match ret_mode:
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
        linecount = len(linelist)

        for i in range(linecount):
            line = linelist[i].strip()
            error_context = f'file {sqlfile}, line {i + 1}: {line}'
            if line[0:3] == '--!':
                method_json = None 
                try: method_json = json.loads(line[3:])
                except: pass
                if not method_json:
                    raise Exception (f'Invalid JSON, {error_context}')
                if (
                    len(method_json) != 3
                    or not 'name' in method_json or not re.search(r'^[a-z_A-Z]\w+$', method_json['name'])
                    or not 'returns' in method_json or not method_json['returns'] in ('recordset', 'record', 'value', 'none')
                    or not 'param_mode' in method_json or not method_json['param_mode'] in ('named', 'positional', 'none')
                   ):
                    raise Exception (f'Invalid method specifier, {error_context}')

                method_name = method_json['name']
                this.__method_wh[method_name] = {'sql':'', 'returns':method_json['returns'], 'param_mode':method_json['param_mode']}
                setattr(this.__class__, method_name, this.__method_factory(method_name))
                continue

            if line == '' or line[0:2] == '--': continue
            if not method_name:
                raise Exception (f'Syntax error, {error_context}')
            else:
                this.__method_wh[method_name]['sql'] += linelist[i]

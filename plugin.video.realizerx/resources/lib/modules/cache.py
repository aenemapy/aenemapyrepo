# -*- coding: utf-8 -*-

import ast
import hashlib
import re
import time
from resources.lib.modules import control
from ast import literal_eval
from hashlib import md5
from re import sub as re_sub

try:
    from sqlite3 import dbapi2 as db, OperationalError
except ImportError:
    from pysqlite2 import dbapi2 as db, OperationalError

"""
This module is used to get/set cache for every action done in the system
"""

cache_table = 'cache'
cache_table_string = 'cache_string'


def get(function, duration, *args):
    """
    :param function: Function to be executed
    :param duration: Duration of validity of cache in hours
    :param args: Optional arguments for the provided function
    """
    try:
        key = _hash_function(function, args)
        cache_result = cache_get(key)
        if cache_result:
            result = literal_eval(cache_result['value'])
            #print ("NEW CACHE RESULT %s " % result)
            if _is_cache_valid(cache_result['date'], duration):
                #print ("RETURNING VALID CACHE")
                return result

        fresh_result = repr(function(*args))
        try:  # Sometimes None is returned as a string instead of None type for "fresh_result"
            invalid = False
            if not fresh_result: invalid = True
            elif fresh_result == 'None' or fresh_result == '' or fresh_result == '[]' or fresh_result == '{}': invalid = True
            elif len(fresh_result) == 0: invalid = True
        except: pass

        if invalid: # If the cache is old, but we didn't get "fresh_result", return the old cache
            if cache_result: return result
            else: return None
        else:
            cache_insert(key, fresh_result)
            return literal_eval(fresh_result)
    except:

        return None
        
        
        
def get_from_string(key, duration, data, update=False):
    try:
        if update == False: raise Exception()
        r = cache_update(key, str(data))
        return data
    except:
        pass
    try:
        if update != False: raise Exception()
        cache_result = cache_get(key)
        if cache_result:
            if _is_cache_valid(cache_result['date'], duration):
                return ast.literal_eval(cache_result['value'])
        if data == None: return None # UPDATE CACHE NOW
        cache_update(key, str(data))
        return data
    except Exception:
        return None
        
def cache_update(key, value):
    try:
        cursor = _get_connection_cursor()
        now = int(time.time())
        cursor.execute("DELETE FROM %s WHERE key = ?" % cache_table, [key])
        cursor.execute("CREATE TABLE IF NOT EXISTS %s (key TEXT, value TEXT, date INTEGER, UNIQUE(key))" % cache_table) 
        cursor.execute("INSERT INTO %s Values (?, ?, ?)" % cache_table, (key, value, now))
        cursor.connection.commit()
        return True
    except OperationalError:
        return None
        
def timeout(function, *args):
    try:
        key = _hash_function(function, args)
        result = cache_get(key)
        print ("CACHE TIMEOUT", result)
        return int(result['date'])
    except Exception:
        return None


def cache_get(key):
    # type: (str, str) -> dict or None
    try:
        cursor = _get_connection_cursor()
        cursor.execute("SELECT * FROM %s WHERE key = ?" % cache_table, [key])
        return cursor.fetchone()
    except OperationalError:
        return None


def cache_insert(key, value):
    # type: (str, str) -> None
    cursor = _get_connection_cursor()
    now = int(time.time())
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS %s (key TEXT, value TEXT, date INTEGER, UNIQUE(key))"
        % cache_table
    )
    update_result = cursor.execute(
        "UPDATE %s SET value=?,date=? WHERE key=?"
        % cache_table, (value, now, key))

    if update_result.rowcount is 0:
        cursor.execute(
            "INSERT INTO %s Values (?, ?, ?)"
            % cache_table, (key, value, now)
        )

    cursor.connection.commit()


def cache_clear():
    try:
        cursor = _get_connection_cursor()

        for t in [cache_table, 'rel_list', 'rel_lib']:
            try:
                cursor.execute("DROP TABLE IF EXISTS %s" % t)
                cursor.execute("VACUUM")
                cursor.commit()
            except:
                pass
    except:
        pass


def _get_connection_cursor():
    conn = _get_connection()
    return conn.cursor()


def _get_connection():
    control.makeFile(control.dataPath)
    conn = db.connect(control.cacheFile)
    conn.row_factory = _dict_factory
    return conn


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def _hash_function(function_instance, *args):
    #print ("NEW FUNCTION NAME")
    #print (_get_function_name(function_instance))
    #print (args)
    return _get_function_name(function_instance) + _generate_md5(args)


def _get_function_name(function_instance):
    return re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(function_instance))


def _generate_md5(*args):

    md5_hash = hashlib.md5()

    [md5_hash.update(str(arg).encode('utf-8')) for arg in args]

    return str(md5_hash.hexdigest())


def _is_cache_valid(cached_time, cache_timeout):
    now = int(time.time())
    diff = now - cached_time
    #print ("CACHE VALID")
    #print ((cache_timeout * 3600) > diff)
    return (cache_timeout * 3600) > diff

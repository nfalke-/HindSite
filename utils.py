'''
a few utility functions
'''
import os
from collections import namedtuple
import MySQLdb
from config import db_auth

task = namedtuple('task', [
    'action',
    'is_optional',
    'args',
    'take_screenshot',
    'screenshot_name',
    'threshold'
    ])


def makedir(dirname: str) -> None:
    '''creates a directory if one doesn't already exist'''
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


def get_from_db(query: str, args=()) -> tuple:
    '''
    gets rows from the db using a SELECT query
    '''
    database = MySQLdb.connect(**db_auth)
    cursor = database.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.execute(query, args)
    results = cursor.fetchall()
    if results:
        return results
    return ()


def write_to_db(query: str, args=()) -> int:
    '''
    writes a row to the db using an INSERT or UPDATE query
    returns the last row affected
    '''
    database = MySQLdb.connect(**db_auth)
    cursor = database.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.execute(query, args)
    database.commit()
    return cursor.lastrowid


def write_many_to_db(query: str, args=()) -> int:
    '''
    writes rows to the db using an INSERT or UPDATE query
    returns the last row affected
    '''
    database = MySQLdb.connect(**db_auth)
    cursor = database.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.executemany(query, args)
    database.commit()
    return cursor.lastrowid

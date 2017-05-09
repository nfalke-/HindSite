import os
from config import db_auth
import MySQLdb
from collections import namedtuple

def makedir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

task = namedtuple('task', [
    'action',
    'args',
    'take_screenshot',
    'screenshot_name',
    'threshold'
    ])



def get_from_db(query, args=()):
    db= MySQLdb.connect(**db_auth)
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.execute(query, args)
    results = cursor.fetchall()
    if results:
        return results
    return ()

def write_to_db(query, args=()):
    db= MySQLdb.connect(**db_auth)
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.execute(query, args)
    db.commit()
    return cursor.lastrowid

def write_many_to_db(query, args=()):
    db= MySQLdb.connect(**db_auth)
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.executemany(query, args)
    db.commit()
    return cursor.lastrowid

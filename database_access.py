import MySQLdb
from config import db_auth

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
    return

def write_many_to_db(query, args=()):
    db= MySQLdb.connect(**db_auth)
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.executemany(query, args)
    db.commit()
    return

def delete_steps_from_test(testid):
    query = '''delete from
        steps
    where
        testid = %s
    '''
    write_to_db(query, (testid))

def get_steps_for_test(testid):
    query = '''select
        action, args
    from
        steps
    left join
        tests
    using(testid)
    where
        tests.testid=%s
    order by
        stepnumber'''
    return get_from_db(query, (testid))

def list_suites():
    query = '''
    select
        suitename, suiteid
    from
        suites
    '''
    return get_from_db(query)

def list_tests(suite_id):
    query = '''
    select
        testname, testid
    from
        tests
    where
        suiteid = %s
    '''
    return get_from_db(query, (suite_id, ))

def add_steps_to_test(testid, steps):
    delete_steps_from_test(testid)
    query = '''insert into
        steps (testid, stepnumber, action, args)
    values
        (%s, %s, %s, %s)'''
    steps = tuple((testid, stepnumber, step[0], step[1]) for stepnumber, step in enumerate(steps, 1))
    print(steps)
    write_many_to_db(query, steps)

def add_suite(name):
    query = """insert into
        suites (suitename)
    values
        (%s)"""
    write_to_db(query, name)

def add_test(suiteid, name):
    query = """insert into
        tests(testname, suiteid)
    values
        (%s, %s)"""
    write_to_db(query, (name, suiteid))

def add_run(testid, runtime):
    query = """insert into
        previousruns(testid, runtime)
    values
        (%s, %s)"""
    write_to_db(query, (testid, runtime))

def get_run_by_id(runid):
    query = '''
    select
        testid, runtime
    from
        previousruns
    where
        runid = %s
    '''
    return get_from_db(query, (runid))[0]

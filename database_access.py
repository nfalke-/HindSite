import MySQLdb
from utils import task
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
    return cursor.lastrowid

def write_many_to_db(query, args=()):
    db= MySQLdb.connect(**db_auth)
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.executemany(query, args)
    db.commit()
    return cursor.lastrowid

def delete_steps_from_test(testid):
    query = '''delete from
        steps
    where
        testid = %s
    '''
    write_to_db(query, (testid))

def get_steps_for_test(testid):
    query = '''select
        action, args, screenshot, screenshot_name, threshold
    from
        steps
    left join
        tests
    using(testid)
    where
        tests.testid=%s
    order by
        stepnumber'''
    return [task(*i) for i in get_from_db(query, (testid))]

def list_suites():
    query = '''
    select
        suitename, suiteid, browser
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
        steps (testid, stepnumber, action, args, screenshot, screenshot_name, threshold)
    values
        (%s, %s, %s, %s, %s, %s, %s)'''
    steps = tuple((testid, stepnumber)+tuple(i for i in step) for stepnumber, step in enumerate(steps, 1))
    write_many_to_db(query, steps)

def add_suite(name, browser):
    query = """insert into
        suites (suitename, browser)
    values
        (%s, %s)"""
    write_to_db(query, (name, browser))

def add_test(suiteid, name):
    query = """insert into
        tests(testname, suiteid)
    values
        (%s, %s)"""
    write_to_db(query, (name, suiteid))

def get_run_by_id(runid):
    query = '''
    select
        testid, runtime
    from
        runs
    where
        runid = %s
    '''
    return get_from_db(query, (runid))[0]

def get_runs(testid):
    query = '''
    select
        runid, start, end, passed, screenshot_passed
    from
        runs
    where
        testid = %s
    '''
    return get_from_db(query, (testid))

def add_run(testid, start):
    query = '''
    insert into
        runs(testid, start)
    values
        (%s, %s);
    '''
    return write_to_db(query, (testid, start))

def update_run(runid, end, passed, screenshot_passed):
    query = '''
    update runs
    set
        end=%s, passed=%s, screenshot_passed=%s
    where
        runid=%s
    '''
    return write_to_db(query, (end, passed, screenshot_passed, runid))

def add_run_step(runid, action, args, passed, take_screenshot,
                 screenshot_percent, screenshot_passed, screenshot_name):
    query = '''
    insert into
        run_step(runid, action, args, passed, take_screenshot,
                 screenshot_percentage, screenshot_passed, screenshot_name)
    values
        (%s, %s, %s, %s, %s, %s, %s, %s);
    '''
    return write_to_db(query, (runid, action, args, passed, take_screenshot,
                               screenshot_percent, screenshot_passed, screenshot_name))

def get_steps_for_run(runid):
    query = '''
    select
        action, args, passed, take_screenshot, screenshot_percentage, screenshot_passed, screenshot_name
    from
        run_step
    where
        runid = %s
    '''
    return get_from_db(query, (runid))

def get_most_recent_run_state(testid):
    query = '''
    select
        passed, screenshot_passed, start
    from
        runs
    where
        testid = %s
    order by
        runid desc
    limit 1
    '''
    return get_from_db(query, (testid))

def get_browser_for_suite(suiteid):
    query = '''
    select
        browser
    from
        suites
    where
        suiteid = %s
    '''
    return get_from_db(query, (suiteid))


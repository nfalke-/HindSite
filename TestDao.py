from utils import get_from_db, write_to_db, write_many_to_db
from utils import task

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

def add_test(suiteid, name):
    query = """insert into
        tests(testname, suiteid)
    values
        (%s, %s)"""
    write_to_db(query, (name, suiteid))


def delete_steps_from_test(testid):
    query = '''delete from
        steps
    where
        testid = %s
    '''
    write_to_db(query, (testid))

def add_steps_to_test(testid, steps):
    delete_steps_from_test(testid)
    query = '''insert into
        steps (testid, stepnumber, action, args, screenshot, screenshot_name, threshold)
    values
        (%s, %s, %s, %s, %s, %s, %s)'''
    steps = tuple((testid, stepnumber)+tuple(i for i in step) for stepnumber, step in enumerate(steps, 1))
    write_many_to_db(query, steps)


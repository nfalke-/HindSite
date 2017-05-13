from utils import get_from_db, write_to_db, write_many_to_db
from utils import task

def get_name_from_id(test_id):
    query = '''
    select
        testname
    from
        tests
    where
        testid = %s
    '''
    rows = get_from_db(query, (test_id, ))
    if rows:
        if rows[0]:
            return rows[0][0]
    return None

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
    return write_to_db(query, (name, suiteid))

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


def copy_test(new_suite_id, old_test_id):
    new_name = get_name_from_id(old_test_id)+'{}'
    name_list = {i[0] for i in list_tests(new_suite_id)}
    end = ''
    if new_name.format(end) in name_list:
        end = ' (copy)'
        if new_name.format(end) in name_list:
            copy_number = 1
            end = ' (copy {})'.format(copy_number)
            while new_name.format(end) in name_list:
                copy_number += 1
                end = ' (copy {})'.format(copy_number)
    new_name = new_name.format(end)
    new_test_id = add_test(new_suite_id, new_name)
    add_steps_to_test(new_test_id, get_steps_for_test(old_test_id))

def get_full_test_info(suite_id):
    test_base_info = list_tests(suite_id)
    tests = []
    for test in test_base_info:
        run_state = get_most_recent_run_state(test[1])
        if len(run_state) > 0:
            tests.append(test + run_state[0])
        else:
            tests.append(test + (0, 0, 'never'))
    return tests

def delete_test(test_id):
    query = '''
    delete from
        tests
    where
        testid = %s
    '''
    write_to_db(query, (test_id))

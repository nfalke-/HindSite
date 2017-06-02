'''
Data access module for runs
'''
from utils import get_from_db, write_to_db, write_many_to_db
from utils import task


def get_name_from_id(test_id: int) -> str:
    '''uses a test id to get the name of a test'''
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


def list_tests(suite_id: int) -> tuple:
    '''uses a suite id to list out all tests in that suite'''
    query = '''
    select
        testname, testid
    from
        tests
    where
        suiteid = %s
    '''
    return get_from_db(query, (suite_id, ))


def get_most_recent_run_state(testid: int) -> tuple:
    '''gets the state of the most recent run for a test'''
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


def get_steps_for_test(testid: int) -> tuple:
    '''returns all the steps in a test'''
    query = '''select
        action, optional, args, screenshot, screenshot_name, threshold
    from
        steps
    left join
        tests
    using(testid)
    where
        tests.testid=%s
    order by
        stepnumber'''
    return tuple(task(*i) for i in get_from_db(query, (testid)))


def add_schedule(suite_id: int, test_id: int, active: bool, period: int) -> int:
    if not active:
        period = 0
    query = """insert into
        scheduledTest (suiteid, testid, active, period, nextrun)
    values
        (%s, %s, %s, %s, now() + interval %s minute)"""
    return write_to_db(query, (suite_id, test_id, active, period, period))


def add_test(suite_id: int, name: str, active: bool, period: int) -> int:
    '''adds a test to the database'''
    query = """insert into
        tests(testname, suiteid)
    values
        (%s, %s)"""
    test_id = write_to_db(query, (name, suite_id))
    add_schedule(suite_id, test_id, active, period)
    return test_id


def delete_steps_from_test(testid: int) -> int:
    '''
    deletes all steps from a test
    (used when editing steps, because it's easier than updating each step)
    '''
    query = '''delete from
        steps
    where
        testid = %s
    '''
    return write_to_db(query, (testid))


def update_name(testid: int, name: str) -> int:
    '''changes the name of a test in the database'''
    query = '''update
        tests
    set testname = %s
    where
        testid = %s
    '''
    return write_to_db(query, (name, testid))


def add_steps_to_test(testid: int, steps: tuple) -> None:
    '''adds steps to a test (deletes all of the previous steps first)'''
    delete_steps_from_test(testid)
    query = '''insert into
        steps (testid, stepnumber, action, optional, args, screenshot, screenshot_name, threshold)
    values
        (%s, %s, %s, %s, %s, %s, %s, %s)'''
    steps = tuple((testid, stepnumber)+tuple(i for i in step)
                  for stepnumber, step in enumerate(steps, 1))
    write_many_to_db(query, steps)


def copy_test(new_suite_id: int, old_test_id: int) -> None:
    '''copies a test to a new suite (or the same suite)'''
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
    new_test_id = add_test(new_suite_id, new_name, False, 0)
    add_steps_to_test(new_test_id, get_steps_for_test(old_test_id))


def get_full_test_info(suite_id: int) -> list:
    '''lists out all testsm and includes the most recent run state for each test'''
    test_base_info = list_tests(suite_id)
    tests = []
    for test in test_base_info:
        run_state = get_most_recent_run_state(test[1])
        if run_state:
            tests.append(test + run_state[0])
        else:
            tests.append(test + (0, 0, 'never'))
    return tests


def delete_test(test_id: int) -> int:
    '''recursively delete an entire test'''
    query = '''
    delete from
        tests
    where
        testid = %s
    '''
    return write_to_db(query, (test_id))


def get_tests_scheduled_later_than_now() -> tuple:
    '''
    gets tests that are scheduled to run later than now
    '''
    query = '''
    select
        id, suiteid, testid
    from
        scheduledTest
    where
        nextrun < now()
    '''
    return get_from_db(query)


def schedule_next_test(schedule_id: int) -> int:
    '''
    schedules a test to run either at the last scheduled time + the period,
    or at now + the period\
    '''
    query = '''
    update
        scheduledTest
    set
        nextrun = if(
            nextrun + interval period minute > now(),
            nextrun + interval period minute,
            now() + interval period minute
        )
    where
        id = %s
    '''
    return write_to_db(query, (schedule_id))


def get_schedule_config(suite_id: int, test_id: int) -> tuple:
    '''
    gets the configurable fields from a scheduled test
    '''
    query = '''
    select
        period
    from
        scheduledTest
    where
        suiteid = %s
        and testid = %s
    '''
    return get_from_db(query, (suite_id, test_id))


def update_schedule_config(suite_id: int, test_id: int, active: bool, period: int) -> tuple:
    '''gets the configurable fields from a scheduled suite'''
    query = '''
    update
        scheduledTest
    set
        active=%s, period=%s
    where
        suiteid = %s
        and testid = %s
    '''
    return (True, write_to_db(query, (active, period, suite_id, test_id))) or (False, 0)

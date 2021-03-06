'''
Data Access module for suites
'''
from utils import get_from_db, write_to_db
from Daos import TestDao


def get_suite(suite_id: int) -> tuple:
    '''return the suite name and description from the db using the suite id'''
    query = '''
    select
        suitename, description
    from
        suites
    where
        suiteid = %s
    '''
    rows = get_from_db(query, (suite_id, ))
    if rows:
        return rows[0]
    return None


def get_name_from_id(suite_id: int) -> str:
    '''get the name of the suite from the suite id'''
    query = '''
    select
        suitename
    from
        suites
    where
        suiteid = %s
    '''
    rows = get_from_db(query, (suite_id, ))
    if rows:
        if rows[0]:
            return rows[0][0]
    return None


def get_description_from_id(suite_id: int) -> str:
    '''get the description of the suite using the suite id'''
    query = '''
    select
        description
    from
        suites
    where
        suiteid = %s
    '''
    rows = get_from_db(query, (suite_id, ))
    if rows:
        if rows[0]:
            return rows[0][0]
    return None


def list_suites() -> tuple:
    '''list out all the suites in the database'''
    query = '''
    select
        suitename, suiteid, description, browser, width, height
    from
        suites
    join
        suite_config
    using(suiteid)
    '''
    return get_from_db(query)


def add_config(suite_id: int, browser: str, width: int, height: int) -> int:
    '''add configuration to a suite'''
    query = """insert into
        suite_config (suiteid, browser, width, height)
    values
        (%s, %s, %s, %s)"""
    return write_to_db(query, (suite_id, browser, width, height))


def add_schedule(suite_id: int, active: bool, period: int) -> int:
    if not active:
        period = 0
    query = """insert into
        scheduledSuite (suiteid, active, period, nextrun)
    values
        (%s, %s, %s, now() + interval %s minute)"""
    return write_to_db(query, (suite_id, active, period, period))


def add_suite(name: str, description: str, browser: str, width: int,
              height: int, active: bool, period: int) -> int:
    '''add a suite to the database'''
    query = """insert into
        suites (suitename, description)
    values
        (%s, %s)"""
    suite_id = write_to_db(query, (name, description))
    add_config(suite_id, browser, width, height)
    add_schedule(suite_id, active, period)
    return suite_id


def delete_suite(suite_id: int) -> None:
    '''delete a suite from the database'''
    query = """delete from
        suites
    where
        suiteid = %s
    """
    write_to_db(query, (suite_id))


def get_settings_for_suite(suiteid: int) -> tuple:
    '''get the configuration settings for a suite from the database'''
    query = '''
    select
        browser, width, height
    from
        suite_config
    where
        suiteid = %s
    '''
    rows = get_from_db(query, (suiteid))
    if rows:
        return rows[0]
    return None


def update_suite_settings(suite_id: int, browser: str, width: int, height: int) -> None:
    '''update the configuration settings for a suite'''
    query = """
    update
        suite_config
    set
        browser = %s,
        width = %s,
        height = %s
    where
        suiteid = %s
    """
    write_to_db(query, (browser, width, height, suite_id))


def update_suite(suite_id: int, name: str, description: str) -> None:
    '''update a suite name and description'''
    query = """
    update
        suites
    set
        suitename = %s,
        description = %s
    where
        suiteid = %s"""
    write_to_db(query, (name, description, suite_id))


def copy_suite(old_suite_id: int) -> None:
    '''copy an entire suite recursively (all tests and steps get copied as well)'''
    new_name = get_name_from_id(old_suite_id)+'{}'
    name_list = {i[0] for i in list_suites()}
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
    browser, width, height = get_settings_for_suite(old_suite_id)
    active, period = get_schedule_config(old_suite_id)
    description = get_description_from_id(old_suite_id)
    tests = [i[1] for i in TestDao.list_tests(old_suite_id)]
    new_suite_id = add_suite(new_name, description, browser, width, height, active, period)
    for test_id in tests:
        TestDao.copy_test(new_suite_id, test_id)


def get_most_recent_run_state(suite_id: int) -> tuple:
    '''get the most recent run from the most recently ran test'''
    query = '''
    select
        start
    from
        runs
    join
        tests
    using(testid)
    join
        suites
    using(suiteid)
    where
        suiteid = %s
    order by
        runid desc
    limit 1
    '''
    return get_from_db(query, (suite_id))


def get_test_count(suite_id: int) -> tuple:
    '''count the tests in a suite'''
    query = '''
    select
        count(*)
    from
        tests
    join
        suites
    using(suiteid)
    where
        suiteid = %s
    '''
    return get_from_db(query, (suite_id))


def get_suites_scheduled_later_than_now() -> tuple:
    '''
    gets tests and suites that are scheduled to run later than now
    '''
    query = '''
    select
        id, suiteid
    from
        scheduledSuite
    where
        nextrun < now()
        and active
    '''
    return get_from_db(query)


def schedule_next_suite(schedule_id: int) -> int:
    '''
    schedules a test to run either at the last scheduled time + the period,
    or at now + the period
    '''
    query = '''
    update
        scheduledSuite
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


def get_schedule_config(suite_id: int) -> tuple:
    '''gets the configurable fields from a scheduled suite'''
    query = '''
    select
        active, period
    from
        scheduledSuite
    where
        suiteid = %s
    '''
    return get_from_db(query, (suite_id))[0] or (False, 0)


def update_schedule_config(suite_id: int, active: bool, period: int) -> tuple:
    '''gets the configurable fields from a scheduled suite'''
    query = '''
    update
        scheduledSuite
    set
        active=%s, period=%s
    where
        suiteid = %s
    '''
    return (True, write_to_db(query, (active, period, suite_id))) or (False, 0)

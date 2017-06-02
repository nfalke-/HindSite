'''
Data access module for runs
'''
from utils import get_from_db, write_to_db


def get_runs(testid: int) -> tuple:
    '''
    gets all runs using a test id
    '''
    query = '''
    select
        runid, start, end, passed, screenshot_passed
    from
        runs
    where
        testid = %s
    '''
    return get_from_db(query, (testid))


def get_steps_for_run(runid: int) -> tuple:
    '''
    gets all steps for a run using a run id
    '''
    query = '''
    select
        action, args, passed, take_screenshot,
        screenshot_percentage, screenshot_passed, screenshot_name
    from
        run_step
    where
        runid = %s
    '''
    return get_from_db(query, (runid))


def add_run(testid: int, start: str) -> int:
    '''
    adds a run to the database
    used when a test starts
    '''
    query = '''
    insert into
        runs(testid, start)
    values
        (%s, %s);
    '''
    return write_to_db(query, (testid, start))


def update_run(runid: int, end: str, passed: bool, screenshot_passed: bool) -> int:
    '''
    updates a run in the database
    used after a test completes
    '''
    query = '''
    update runs
    set
        end=%s, passed=%s, screenshot_passed=%s
    where
        runid=%s
    '''
    return write_to_db(query, (end, passed, screenshot_passed, runid))


def add_run_step(runid: int, action: str, args: str, passed: bool, take_screenshot: bool,
                 screenshot_percent: float, screenshot_passed: bool, screenshot_name: str) -> int:
    '''
    adds a step to a run
    '''
    query = '''
    insert into
        run_step(runid, action, args, passed, take_screenshot,
                 screenshot_percentage, screenshot_passed, screenshot_name)
    values
        (%s, %s, %s, %s, %s, %s, %s, %s);
    '''
    return write_to_db(query, (runid, action, args, passed, take_screenshot,
                               screenshot_percent, screenshot_passed, screenshot_name))

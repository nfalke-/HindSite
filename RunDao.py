from utils import get_from_db, write_to_db, write_many_to_db

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


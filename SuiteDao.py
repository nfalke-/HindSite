from utils import get_from_db, write_to_db, write_many_to_db
import TestDao


def get_name_from_id(suite_id):
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

def get_description_from_id(suite_id):
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

def list_suites():
    query = '''
    select
        suitename, suiteid, browser, description
    from
        suites
    '''
    return get_from_db(query)

def add_suite(name, browser, description):
    query = """insert into
        suites (suitename, browser, description)
    values
        (%s, %s, %s)"""
    return write_to_db(query, (name, browser, description))

def delete_suite(suite_id):
    query = """delete from
        suites
    where
        suiteid = %s
    """
    write_to_db(query, (suite_id))

def get_browser_for_suite(suiteid):
    query = '''
    select
        browser
    from
        suites
    where
        suiteid = %s
    '''
    rows = get_from_db(query, (suiteid))
    if rows:
        if rows[0]:
            return rows[0][0]
    return None

def copy_suite(old_suite_id):
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
    browser = get_browser_for_suite(old_suite_id)
    description = get_description_from_id(old_suite_id)
    tests = [i[1] for i in TestDao.list_tests(old_suite_id)]
    new_suite_id = add_suite(new_name, browser, description)
    for test_id in tests:
        TestDao.copy_test(new_suite_id, test_id)


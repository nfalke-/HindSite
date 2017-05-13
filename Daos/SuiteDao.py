from utils import get_from_db, write_to_db, write_many_to_db
from Daos import TestDao


def get_suite(suite_id):
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
        suitename, suiteid, description, browser, width, height
    from
        suites
    join
        suite_config
    using(suiteid)
    '''
    return get_from_db(query)

def add_config(suite_id, browser, width, height):
    query = """insert into
        suite_config (suiteid, browser, width, height)
    values
        (%s, %s, %s, %s)"""
    suite_id = write_to_db(query, (suite_id, browser, width, height))

def add_suite(name, description, browser, width, height):
    query = """insert into
        suites (suitename, description)
    values
        (%s, %s)"""
    suite_id = write_to_db(query, (name, description))
    add_config(suite_id, browser, width, height)
    return suite_id

def delete_suite(suite_id):
    query = """delete from
        suites
    where
        suiteid = %s
    """
    write_to_db(query, (suite_id))

def get_settings_for_suite(suiteid):
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

def update_suite_settings(suite_id, browser, width, height):
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

def update_suite(suite_id, name, description):
    query = """
    update
        suites
    set
        suitename = %s,
        description = %s
    where
        suiteid = %s"""
    print(description)
    write_to_db(query, (name, description, suite_id))


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
    browser, width, height = get_settings_for_suite(old_suite_id)
    description = get_description_from_id(old_suite_id)
    tests = [i[1] for i in TestDao.list_tests(old_suite_id)]
    new_suite_id = add_suite(new_name, description, browser, width, height)
    for test_id in tests:
        TestDao.copy_test(new_suite_id, test_id)


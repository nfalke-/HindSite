from utils import get_from_db, write_to_db, write_many_to_db

def list_suites():
    query = '''
    select
        suitename, suiteid, browser
    from
        suites
    '''
    return get_from_db(query)

def add_suite(name, browser):
    query = """insert into
        suites (suitename, browser)
    values
        (%s, %s)"""
    write_to_db(query, (name, browser))

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

import MySQLdb

def get_from_db(query, args=()):
    db= MySQLdb.connect(host="localhost", user="diffmaster",
                        passwd="hunter2", db="sitediff")
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.execute(query, args)
    results = cursor.fetchall()
    if results:
        return results
    return ()

def write_to_db(query, args=()):
    db= MySQLdb.connect(host="localhost", user="diffmaster",
                        passwd="hunter2", db="sitediff")
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.execute(query, args)
    db.commit()
    return

def write_many_to_db(query, args=()):
    db= MySQLdb.connect(host="localhost", user="diffmaster",
                        passwd="hunter2", db="sitediff")
    cursor = db.cursor()
    if not isinstance(args, tuple):
        args = (args, )
    cursor.executemany(query, args)
    db.commit()
    return

def delete_steps_from_test(testid):
    query = '''delete from
        steps
    where
        testid = %s
    '''
    write_to_db(query, (testid))

def get_steps_for_test(testid):
    query = '''select
        action, args
    from
        steps
    left join
        tests
    using(testid)
    where
        tests.testid=%s
    order by
        stepnumber'''
    return get_from_db(query, (testid))

def add_steps_to_test(testid, steps):
    delete_steps_from_test(testid)
    query = '''insert into
        steps (testid, stepnumber, action, args)
    values
        (%s, %s, %s, %s)'''
    steps = tuple((testid, stepnumber, step[0], step[1]) for stepnumber, step in enumerate(steps, 1))
    write_many_to_db(query, steps)


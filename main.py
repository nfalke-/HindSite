'''
Main module, runs the website
'''
from decimal import Decimal
from shutil import copyfile
import os
from Daos import SuiteDao, TestDao, RunDao
from flask import Flask, render_template, request, redirect, url_for, jsonify
import flask
from config import config
import navigator
from redis import Redis
from rq import Queue

q = Queue(connection=Redis('localhost', 6379))
app = Flask(__name__)


def is_int(s: str) -> bool:
    '''returns true if s can be converted to int, false otherwise'''
    try:
        int(s)
        return True
    except ValueError:
        return False


def json_safe(value: object) -> object:
    '''converts values to json safe values'''
    if isinstance(value, Decimal):
        return float(value)
    return value


# view
@app.route('/', methods=['GET'])
def index() -> str:
    '''for list of suites'''
    suites = SuiteDao.list_suites()
    return render_template('view/root.html', suites=suites)


@app.route('/suites/<suite_id>/', methods=['GET'])
def view_suite(suite_id: int) -> str:
    '''for list of tests'''
    suites = SuiteDao.list_suites()
    tests = TestDao.get_full_test_info(suite_id)
    return render_template(
        'view/suite.html', tests=tests,
        suites=suites, suite_id=suite_id
    )


@app.route('/suites/<suite_id>/tests/<test_id>/', methods=['GET'])
def view_test(suite_id: int, test_id: int) -> str:
    '''for list of steps and runs'''
    steps = TestDao.get_steps_for_test(test_id)
    runs = RunDao.get_runs(test_id)
    return render_template('view/test.html', suite_id=suite_id,
                           test_id=test_id, steps=steps, runs=runs)


@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/', methods=['GET'])
def view_run(suite_id: int, test_id: int, run_id: int) -> str:
    '''shows an individual run'''
    steps = RunDao.get_steps_for_run(run_id)
    return render_template('view/run.html', suite_id=suite_id,
                           test_id=test_id, run_id=run_id, steps=steps)


# api
@app.route('/data/', methods=['GET'])
def index_api() -> flask.wrappers.Response:
    '''gives information for suites view in json format'''
    suites = []  # type: list
    for suite in SuiteDao.list_suites():
        suites += [
            suite +
            (SuiteDao.get_most_recent_run_state(suite[1]) or ('never', )) +
            (SuiteDao.get_test_count(suite[1]) or (0, ))
        ]
    return jsonify(suites)


@app.route('/suites/<suite_id>/data/', methods=['GET'])
def suite_api(suite_id: int) -> flask.wrappers.Response:
    '''gives information for tests view in json format'''
    tests = TestDao.get_full_test_info(suite_id)
    tests = [[json_safe(i) for i in j] for j in tests]
    return jsonify(tests)


@app.route('/suites/<suite_id>/tests/<test_id>/data/', methods=['GET'])
def test_api(suite_id: int, test_id: int) -> flask.wrappers.Response:
    '''gives information for runs and step view in json format'''
    steps = TestDao.get_steps_for_test(test_id)
    runs = RunDao.get_runs(test_id)
    data = {
        "suite": suite_id,
        "test": test_id,
        "steps": [[json_safe(i) for i in j] for j in steps],
        "runs": [[json_safe(i) for i in j] for j in runs]
    }
    return jsonify(data)


@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/data/', methods=['GET'])
def run_api(suite_id: int, test_id: int, run_id: int) -> flask.wrappers.Response:
    '''gives information for single-run view in json format'''
    steps = RunDao.get_steps_for_run(run_id)
    steps = tuple([json_safe(i) for i in j] for j in steps)
    return jsonify(steps)


# add forms
@app.route('/suites/add/', methods=['GET'])
def add_suite() -> str:
    '''
        renders the form for adding a new suite
    '''
    return render_template('add/suite.html')


@app.route('/suites/<suite_id>/tests/add/', methods=['GET'])
def add_test(suite_id: int) -> str:
    '''
        renders the form for adding a new test
    '''
    return render_template('add/test.html', suite_id=suite_id)


# post add
@app.route('/suites/add/', methods=['POST'])
def post_add_suite():
    '''
        adds a new suite to the database
    '''
    if request.form.get('suitename'):
        name = request.form.get('suitename')
        browser = request.form.get('browser')
        description = request.form.get('description')
        width = request.form.get('width')
        height = request.form.get('height')
        SuiteDao.add_suite(name, description, browser, width, height, False, 0)
        return redirect(url_for('index'))


@app.route('/suites/<suite_id>/tests/add/', methods=['POST'])
def post_add_test(suite_id: int):
    '''
        adds a new test to the database
    '''
    if request.form.get('testname'):
        active = False
        period = 0
        TestDao.add_test(suite_id, request.form.get('testname'), active, period)
        return redirect(url_for('view_suite', suite_id=suite_id))


# edit forms
@app.route('/suites/<suite_id>/tests/<test_id>/edit/', methods=['GET'])
def edit_test(suite_id: int, test_id: int) -> str:
    '''
        form for editing a test
    '''
    name = TestDao.get_name_from_id(test_id)
    steps = TestDao.get_steps_for_test(test_id)
    steps = tuple((i, ) + step for i, step in enumerate(steps, 1))
    if not steps:
        steps = ((1, '', False, '', False, '', .10000), )
    return render_template(
        'edit/test.html',
        suite_id=suite_id, test_id=test_id,
        steps=steps, name=name
    )


@app.route('/suites/<suite_id>/edit/', methods=['GET'])
def edit_suite(suite_id: int) -> str:
    '''
        form for editing a suite
    '''
    browser, width, height = SuiteDao.get_settings_for_suite(suite_id)
    suite_name, description = SuiteDao.get_suite(suite_id)
    scheduled, interval = SuiteDao.get_schedule_config(suite_id)
    return render_template(
        'edit/suite.html',
        suite_name=suite_name,
        suite_id=suite_id,
        description=description,
        browser=browser,
        width=width,
        height=height,
        scheduled=scheduled,
        interval=interval
        )


# post edit
@app.route('/suites/<suite_id>/tests/<test_id>/edit/', methods=['POST'])
def post_edit_test(suite_id: int, test_id: int):
    '''
        edit a test
    '''
    actions = request.form.getlist('action')
    optional = [False]*len(actions)
    checked = set(map(int, request.form.getlist('screenshot')))
    screenshots = [i in checked for i in range(1, len(actions)+1)]
    name = request.form.get('name')
    steps = tuple(zip(
        request.form.getlist('action'),
        optional,
        request.form.getlist('arguments'),
        screenshots,
        request.form.getlist('screenshot_name'),
        request.form.getlist('threshold')
    ))
    TestDao.add_steps_to_test(test_id, steps)
    TestDao.update_name(test_id, name)
    return redirect(url_for('view_test', suite_id=suite_id, test_id=test_id))


@app.route('/suites/<suite_id>/edit/', methods=['POST'])
def post_edit_suite(suite_id: int):
    '''
        edit a suite
    '''
    suite_name = request.form.get('suitename')
    description = request.form.get('description')
    browser = request.form.get('browser')
    width = request.form.get('width')
    height = request.form.get('height')
    if SuiteDao.get_schedule_config(suite_id)[1]:
        print("config exists")
    scheduled = request.form.get('scheduled')
    interval = request.form.get('interval')
    if is_int(interval):
        if int(interval) > 0:
            SuiteDao.update_schedule_config(
                suite_id, bool(scheduled), int(interval))
    SuiteDao.update_suite_settings(suite_id, browser, width, height)
    SuiteDao.update_suite(suite_id, suite_name, description)
    return redirect(url_for('view_suite', suite_id=suite_id))


# run
@app.route('/suites/<suite_id>/tests/<test_id>/run/', methods=['GET'])
def run_test(suite_id: int, test_id: int):
    '''run a test'''
    browser, width, height = SuiteDao.get_settings_for_suite(suite_id)
    q.enqueue(navigator.run_test, test_id, (width, height), browser)
    return redirect(url_for('view_test', suite_id=suite_id, test_id=test_id))


@app.route('/suites/<suite_id>/run/', methods=['GET'])
def run_suite(suite_id: int):
    '''run an entire suite'''
    tests = TestDao.list_tests(suite_id)
    for test in tests:
        run_test(suite_id, test[1])
    return redirect(url_for('view_suite', suite_id=suite_id))


# copy
@app.route('/suites/copy/', methods=['POST'])
def copy_suite():
    '''copy an entire suite'''
    suite = request.form.get('suite')
    SuiteDao.copy_suite(suite)
    return redirect(url_for('index'))


@app.route('/suites/<suite_id>/tests/copy/', methods=['POST'])
def copy_test(suite_id: int):
    '''copy a test from one suite to another (or the same suite)'''
    test = request.form.get('test')
    suite = request.form.get('suite')
    TestDao.copy_test(suite, test)
    return redirect(url_for('view_suite', suite_id=suite_id))


# delete
@app.route('/suites/<suite_id>/delete/', methods=['GET'])
def delete_suite(suite_id: int) -> str:
    '''delete an entire suite'''
    SuiteDao.delete_suite(suite_id)
    return "OK"


@app.route('/suites/<suite_id>/tests/<test_id>/delete/', methods=['GET'])
def delete_test(suite_id: int, test_id: int) -> str:
    '''delete a test'''
    TestDao.delete_test(test_id)
    return "OK"


@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/baseline/<name>/', methods=['GET'])
def change_baseline(suite_id: int, test_id: int, run_id: int, name: str) -> str:
    '''change the baseline image for a test'''
    testpath = os.path.join(*(map(str, [config.BASE, test_id, run_id])))
    baseline_path = os.path.join(config.BASE, str(test_id), 'baseline')
    newfile = os.path.join(testpath, name+'.png')
    baseline_file = os.path.join(baseline_path, name+'.png')
    if os.path.isfile(newfile):
        copyfile(newfile, baseline_file)
    return "OK"

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=True)

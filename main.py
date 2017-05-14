from navigator import Navigator
from shutil import copyfile
from multiprocessing import Process
import os
from Daos import SuiteDao, TestDao, RunDao
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask("app")
basedir = '/static/files'

from decimal import Decimal
def json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

#view
@app.route('/', methods=['GET', 'POST'])
def index():
    suites = SuiteDao.list_suites()
    return render_template('view/root.html', suites=suites)

@app.route('/suites/<suite_id>/', methods=['GET', 'POST'])
def view_suite(suite_id):
    suites = SuiteDao.list_suites()
    tests = TestDao.get_full_test_info(suite_id)
    return render_template('view/suite.html', tests=tests, suites=suites, suite_id=suite_id)

@app.route('/suites/<suite_id>/tests/<test_id>/', methods=['GET', 'POST'])
def view_test(suite_id, test_id):
    steps = TestDao.get_steps_for_test(test_id)
    runs = RunDao.get_runs(test_id)
    return render_template('view/test.html', suite_id=suite_id, test_id=test_id, steps=steps, runs=runs)

@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/', methods=['GET', 'POST'])
def view_run(suite_id, test_id, run_id):
    steps = RunDao.get_steps_for_run(run_id)
    return render_template('view/run.html', suite_id=suite_id, test_id=test_id, run_id=run_id, steps=steps)


#api
@app.route('/data/', methods=['GET', 'POST'])
def index_api():
    suites = []
    for suite in SuiteDao.list_suites():
        suites += [suite + SuiteDao.get_most_recent_run_state(suite[1])]
    return jsonify(suites)

@app.route('/suites/<suite_id>/data/', methods=['GET', 'POST'])
def suite_api(suite_id):
    tests = TestDao.get_full_test_info(suite_id)
    tests = [[json_safe(i) for i in j] for j in tests]
    return jsonify(tests)

@app.route('/suites/<suite_id>/tests/<test_id>/data/', methods=['GET', 'POST'])
def test_api(suite_id, test_id):
    steps = TestDao.get_steps_for_test(test_id)
    runs = RunDao.get_runs(test_id)
    data = {
        "steps": [[json_safe(i) for i in j] for j in steps],
        "runs": [[json_safe(i) for i in j] for j in runs]
    }
    return jsonify(data)

@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/data/', methods=['GET', 'POST'])
def run_api(suite_id, test_id, run_id):
    steps = RunDao.get_steps_for_run(run_id)
    steps = [[json_safe(i) for i in j] for j in steps]
    return jsonify(steps)


#add
@app.route('/suites/add/', methods=['GET', 'POST'])
def add_suite():
    if request.method == 'POST':
        if request.form.get('suitename'):
            name = request.form.get('suitename')
            browser = request.form.get('browser')
            description = request.form.get('description')
            width = request.form.get('width')
            height = request.form.get('height')
            SuiteDao.add_suite(name, description, browser, width, height)
            return redirect(url_for('index'))
    return render_template('add/suite.html')

@app.route('/suites/<suite_id>/tests/add/', methods=['GET', 'POST'])
def add_test(suite_id):
    if request.method == 'POST':
        if request.form.get('testname'):
            TestDao.add_test(suite_id, request.form.get('testname'))
            return redirect(url_for('view_suite', suite_id=suite_id))
    return render_template('add/test.html')

#edit
@app.route('/suites/<suite_id>/tests/<test_id>/edit/', methods=['GET', 'POST'])
def edit_test(suite_id, test_id):
    if request.method == 'POST':
        actions = request.form.getlist('action')
        checked = set(map(int, request.form.getlist('screenshot')))
        screenshots = [i in checked for i in range(1, len(actions)+1)]
        name = request.form.get('name')
        steps = zip(
            request.form.getlist('action'),
            request.form.getlist('arguments'),
            screenshots,
            request.form.getlist('screenshot_name'),
            request.form.getlist('threshold')
        )
        TestDao.add_steps_to_test(test_id, steps)
        TestDao.update_name(test_id, name)
        return redirect(url_for('view_test', suite_id=suite_id, test_id=test_id))
    name = TestDao.get_name_from_id(test_id)
    steps = TestDao.get_steps_for_test(test_id)
    steps = [(i, ) + step for i, step in enumerate(steps, 1)]
    if not steps:
        steps = [(1, '', '', False, '', .10000)]
    return render_template('edit/test.html', steps=steps, name=name)

@app.route('/suites/<suite_id>/edit/', methods=['GET', 'POST'])
def edit_suite(suite_id):
    if request.method == 'POST':
        suite_name = request.form.get('suitename')
        description = request.form.get('description')
        browser = request.form.get('browser')
        width = request.form.get('width')
        height = request.form.get('height')
        SuiteDao.update_suite_settings(suite_id, browser, width, height)
        SuiteDao.update_suite(suite_id, suite_name, description)
        return redirect(url_for('view_suite', suite_id=suite_id))

    browser, width, height = SuiteDao.get_settings_for_suite(suite_id)
    suite_name, description = SuiteDao.get_suite(suite_id)

    return render_template(
        'edit/suite.html',
        suite_name=suite_name,
        description=description,
        browser=browser,
        width=width,
        height=height
        )

#run
@app.route('/suites/<suite_id>/tests/<test_id>/run/', methods=['GET', 'POST'])
def run_test(suite_id, test_id):
    browser, width, height = SuiteDao.get_settings_for_suite(suite_id)
    n = Navigator(test_id, width, height, browser=browser)
    Process(target=n.run).start()
    return redirect(url_for('view_test', suite_id=suite_id, test_id=test_id))

@app.route('/suites/<suite_id>/run/', methods=['GET', 'POST'])
def run_suite(suite_id):
    tests = TestDao.list_tests(suite_id)
    for test in tests:
        run_test(suite_id, test[1])
    return redirect(url_for('view_suite', suite_id=suite_id))

#copy
@app.route('/suites/copy/', methods=['GET', 'POST'])
def copy_suite():
    if request.method == 'POST':
        suite = request.form.get('suite')
        SuiteDao.copy_suite(suite)
    return redirect(url_for('index'))

@app.route('/suites/<suite_id>/tests/copy/', methods=['GET', 'POST'])
def copy_test(suite_id):
    if request.method == 'POST':
        test = request.form.get('test')
        suite = request.form.get('suite')
        TestDao.copy_test(suite, test)
    return redirect(url_for('view_suite', suite_id=suite_id))

#delete
@app.route('/suites/<suite_id>/delete/', methods=['GET', 'POST'])
def delete_suite(suite_id):
    SuiteDao.delete_suite(suite_id)
    return 'OK'

@app.route('/suites/<suite_id>/tests/<test_id>/delete/', methods=['GET', 'POST'])
def delete_test(suite_id, test_id):
    TestDao.delete_test(test_id)
    return 'OK'

@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/baseline/<name>/', methods=['GET', 'POST'])
def change_baseline(suite_id, test_id, run_id, name):
    testpath = os.path.join(*(map(str, ['.'+basedir, test_id, run_id])))
    baseline_path = os.path.join('.'+basedir, str(test_id), 'baseline')
    newfile = os.path.join(testpath, name+'.png')
    baseline_file = os.path.join(baseline_path, name+'.png')
    print(newfile)
    if os.path.isfile(newfile):
        copyfile(newfile, baseline_file)
    return "OK"

app.run(host="0.0.0.0", port=8060, debug=True)


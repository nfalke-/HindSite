from navigator import Navigator
from shutil import copyfile
from multiprocessing import Process
import os
import SuiteDao
import TestDao
import RunDao
from flask import Flask, render_template, request, redirect, url_for

app = Flask("app")
basedir = '/static'

#view
@app.route('/')
def index():
    suites = SuiteDao.list_suites()
    return render_template('view/root.html', suites=suites)

@app.route('/suites/<suite_id>/', methods=['GET', 'POST'])
def view_suite(suite_id):
    if request.method == 'POST':
        test = request.form.get('test')
        suite = request.form.get('suite')
        copy_test(suite, test)
    suites = SuiteDao.list_suites()
    tests = TestDao.get_full_test_info(suite_id)
    return render_template('view/suite.html', tests=tests, suites=suites, suiteid=suite_id)

@app.route('/suites/<suite_id>/tests/<test_id>/', methods=['GET', 'POST'])
def view_test(suite_id, test_id):
    steps = TestDao.get_steps_for_test(test_id)
    runs = RunDao.get_runs(test_id)
    return render_template('view/test.html', suiteid=suite_id, testid=test_id, steps=steps, runs=runs)

@app.route('/suites/<suite_id>/tests/<test_id>/runs/<run_id>/', methods=['GET', 'POST'])
def view_run(suite_id, test_id, run_id):
    steps = RunDao.get_steps_for_run(run_id)
    return render_template('view/run.html', suite_id=suite_id, test_id=test_id, run_id=run_id, steps=steps)

#add
@app.route('/suites/add/', methods=['GET', 'POST'])
def add_suite():
    if request.method == 'POST':
        if request.form.get('suitename'):
            name = request.form.get('suitename')
            browser = request.form.get('browser')
            SuiteDao.add_suite(name, browser)
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
        steps = zip(
            request.form.getlist('action'),
            request.form.getlist('arguments'),
            screenshots,
            request.form.getlist('screenshot_name'),
            request.form.getlist('threshold')
        )
        TestDao.add_steps_to_test(test_id, steps)
        return redirect(url_for('view_test', suite_id=suite_id, test_id=test_id))
    steps = TestDao.get_steps_for_test(test_id)
    steps = [(i, ) + step for i, step in enumerate(steps, 1)]
    if not steps:
        steps = [(1, '', '', False, '', .10000)]
    return render_template('edit_steps.html', steps=steps)

#run
@app.route('/suites/<suite_id>/tests/<test_id>/run/', methods=['GET', 'POST'])
def run_test(suite_id, test_id):
    browser = SuiteDao.get_browser_for_suite(suite_id)[0][0]
    n = Navigator(test_id, browser=browser)
    Process(target=n.run).start()
    return redirect(url_for('view_test', suite_id=suite_id, test_id=test_id))

@app.route('/suites/<suite_id>/run/', methods=['GET', 'POST'])
def run_suite(suite_id):
    tests = TestDao.list_tests(suite_id)
    for test in tests:
        run_test(suite_id, test[1])
    return redirect(url_for('view_suite', suite_id=suite_id))

@app.route('/suites/<suite_id>/tests/<test_id>/copy/', methods=['GET', 'POST'])
def copy_test(suite_id, test_id):
    TestDao.copy_test(suite_id, test_id)
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
    if os.path.isfile(newfile):
        copyfile(newfile, baseline_file)
    return "OK"

app.run(host="0.0.0.0", port=8060, debug=True)


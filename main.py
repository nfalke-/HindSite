from navigator import Navigator
import os
import database_access
from flask import Flask, render_template, request, redirect, url_for

app = Flask("app")
basedir = '/static'

@app.route('/')
def index():
    return render_template('root.html', suites=database_access.list_suites())

@app.route('/suites/add/', methods=['GET', 'POST'])
def add_suite():
    if request.method == 'POST':
        if request.form.get('suitename'):
            database_access.add_suite(request.form.get('suitename'))
            return redirect(url_for('index'))
    return render_template('add_suite.html')

@app.route('/tests/add/<suite_id>', methods=['GET', 'POST'])
def add_test(suite_id):
    if request.method == 'POST':
        if request.form.get('testname'):
            database_access.add_test(suite_id, request.form.get('testname'))
            return redirect(url_for('show_tests', suite_id=suite_id))
    return render_template('add_test.html')

@app.route('/suites/<suite_id>', methods=['GET', 'POST'])
def show_tests(suite_id):
    return render_template('tests.html', tests=database_access.list_tests(suite_id), suiteid=suite_id)

@app.route('/tests/<test_id>', methods=['GET', 'POST'])
def show_steps(test_id):
    return render_template('steps.html', testid=test_id, steps=database_access.get_steps_for_test(test_id))

@app.route('/tests/run/<test_id>', methods=['GET', 'POST'])
def run_test(test_id):
    task_list = database_access.get_steps_for_test(test_id)
    n = Navigator(task_list, test_id)
    database_access.add_run(test_id, n.runtime)
    #TODO: thread this
    runtime = n.run()
    return redirect(url_for('show_steps', test_id=test_id))

@app.route('/runs/<run_id>', methods=['GET', 'POST'])
def view_run(run_id):
    testid, runtime = database_access.get_run_by_id(run_id)
    testpath = os.path.join(*(map(str, ['.'+basedir, testid, runtime])))
    print(testpath)
    test_images = []
    for filename in os.listdir(testpath):
        if filename.endswith('.png'):
            test_images.append(os.path.join(testpath, filename))
    return render_template('view_run.html', images=test_images)

@app.route('/tests/edit/<test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    if request.method == 'POST':
        steps = zip(request.form.getlist('action'), request.form.getlist('arguments'))
        print(steps)
        database_access.add_steps_to_test(test_id, steps)
        return redirect(url_for('show_steps', test_id=test_id))
    steps = database_access.get_steps_for_test(test_id)
    steps = [(i, step[0], step[1]) for i, step in enumerate(steps, 1)]
    if not steps:
        steps = [(1, '', '')]
    return render_template('edit_steps.html', steps=steps)

app.run(host="0.0.0.0", port=8080,
        debug=True)

#task_list = (('visit', 'http://www.reddit.com'), )
#if __name__ == '__main__':
#    task_list = database_access.get_steps_for_test(1)
#    n = Navigator(task_list)
#    n.run()

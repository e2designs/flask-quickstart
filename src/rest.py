import os
import sqlite3
from io import StringIO
import csv
import re
from flask_bootstrap import Bootstrap
from wtforms import IntegerField, StringField, SubmitField, SelectField
from flask import Flask, request, render_template, jsonify, make_response
from flask_table import Table, Col
from . import local_db

HTML_ATTRS = {'table border': '1'}
bootstrap = Bootstrap()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
bootstrap.init_app(app)
db = local_db()

def query_bench():
    """ Returns a tuple of bench number and name"""
    query = "SELECT name from bench"
    response = db.local_cur(query)
    values = []
    number = re.compile(r'BENCH(\d+)')
    for bench in response:
        try:
            match = number.search(bench)
            num = match[1]
        except:
            num = 'NULL'
        values.append((num, bench))
    return values

class DynamicForm(FlaskForm):
    """Defines a dynamic dropdown"""
    #benches = query_bench()
    bench = SelectField('bench', choices=[('01', 'BENCH01'), ('05', 'BENCH05')])
    bench_type = SelectField('Type', choices=[])

class Table1(Table):
    column1 = Col('Column 1')
    column3 = Col('Column 3')

class Table2(Table):
    column1 = Col('Value 1')
    column2 = Col('Value 2')
    column3 = Col('Value 3')

class Table3(Table):
    column4 = Col('Error')

@app.route('/')
def index():
    title = 'Flask Quickstart 3.0'
    links = [('/query', 'api_bench', 'Query Bench Information and return json'),
             ('/dynamic', 'Dynamic Form', 'Example flask form with javascript'),
             ('/add', 'Add Bench', 'Add entry form for bench info'),
             ('/populate', 'Populate sometable', 'Populates a dbtable with data'),
             ('/table1', 'Table 1', 'Returns a formatted table with some of the data'),
             ('/table2', 'Table 2', 'Returns a formatted table with all the data'),
             ('/table_error', 'Table Error',
              'Attempts to render table when expected data is not present')]
    return render_template('index.html', title=title, links=links)


@app.route('/dynamic')
def dynamic():
    title = 'Dynamic Form'
    form = DynamicForm()
    query = f"SELECT name, bench_type from bench where name = 'BENCH01'"
    form.bench_type.choices = [(bench_type.id, bench_type.name) for bench in (db.local_cur(query))]
    return render_template('dynamic.html', title=title, form=form)

@app.route('/query')
def query(name='bench'):
    query = f"SELECT * from {name}"
    response = db.local_cur(query)
    return jsonify(response)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Adds values to a database table"""
    title = 'Add Bench info'
    form = BenchForm()
    if request.method == 'POST':
        print(form.name, form.name.__dict__)
        name = form.name.data
        bench_type = form.bench_type.data
        db.local_cur(f"INSERT into bench (name, bench_type) values('BENCH{name:0>2d}', '{bench_type}')")
    return render_template('form.html', title=title, form=form)

@app.route('/populate')
def populate():
    """ Adds a table with data_"""
    name = "sometable"
    columns = ("id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "column1 text, "
               "column2 int, "
               "column3 text")
    db.create_table(name=name, columns=columns)
    for i in range(1, 10):
        data = f"'datapoint{i}', {i}, 'other{i}'"
        db.local_cur(f"INSERT into {name} (column1, column2, column3) values({data})")
    return query(name=name)

@app.route('/table1', methods=['GET', 'POST'])
def table1():
    """ Table output using table template 1"""
    data = db.local_cur('select * from sometable')
    if request.method == 'POST':
        return download_csv(data, filename='table1')
    table = Table1(data, html_attrs=HTML_ATTRS)
    return render_template('table.html', title='Table1 with selective data',
                           table=table)

@app.route('/table2', methods=['GET', 'POST'])
def table2():
    """ Table output using table template 2"""
    data = db.local_cur('select * from sometable')
    if request.method == 'POST':
        return download_csv(data, filename='table2')
    table = Table2(data, html_attrs=HTML_ATTRS)
    return render_template('table.html', title='Table2 with selective data',
                           table=table)

@app.route('/table_error', methods=['GET', 'POST'])
def table_error():
    """ Table output using table template 3"""
    data = db.local_cur('select * from sometable')
    if request.method == 'POST':
        return download_csv(data, filename='table3')
    table = Table3(data, html_attrs=HTML_ATTRS)
    return render_template('table.html', title='Table3 with selective data',
                           table=table)

@app.cli.command()
def test():
    """Executes tests for this application"""
    import pytest
    test_file = os.getenv('TEST_FILES' or '')
    pytest.main(['-vvs', './tests/' + test_file,
                 '--junit-xml=/tmp/results/app_test_results.xml'])

def download_csv(csvList, filename):
    """
    Download csv function
    :param csvList: List of dictionary data
    :param filename: filename prefix to use.
    :returns: Content response with csv file, causes the browser to download the
              csv.
    """
    keys = csvList[0].keys()
    si = StringIO()
    cw = csv.DictWriter(si, keys)
    cw.writeheader()
    cw.writerows(csvList)
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
    response.headers["Content-type"] = "text/csv"
    return response

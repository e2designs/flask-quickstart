import os
import sqlite3
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import IntegerField, StringField, SubmitField
from flask import Flask, request, render_template, jsonify
from . import local_db

bootstrap = Bootstrap()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
bootstrap.init_app(app)
db = local_db()

class BenchForm(FlaskForm):
    """Defines bench entry form"""
    name = IntegerField('Enter Bench number')
    bench_type = StringField('Enter Bench type')
    submit = SubmitField('Submit')

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/query')
def query():
    query = 'SELECT * from bench'
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
        return query()
    return render_template('form.html', title=title, form=form)

@app.cli.command()
def test():
    """Executes tests for this application"""
    import pytest
    test_file = os.getenv('TEST_FILES' or '')
    pytest.main(['-vvs', './tests/' + test_file,
                 '--junit-xml=/tmp/results/app_test_results.xml'])


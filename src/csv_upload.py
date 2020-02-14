import os
import csv
from wtforms import FileField, SelectField
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from flask import Flask, request, render_template, jsonify,  current_app
from flask_bootstrap import Bootstrap
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

bootstrap = Bootstrap()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
app.config['UPLOADED_FOLDER'] = '/tmp/uploads'
bootstrap.init_app(app)

def cur(sql_stmt, col_names=True):
    """
    Database postgres cursor

    :param sql_stmt: - sql statement string to execute
    :returns data: - Dictionary response from the database.

    """
    # minimum and maximum threads to allow.
    min = 5
    max = 50

    HOST = '0.0.0.0'
    SCHEMA = 'testdb'
    PORT = '5444'
    connection_pool = ThreadedConnectionPool(
        min, max,
        host=HOST,
        database=SCHEMA,
        port=PORT,
        user='gate')
    # RealDictCursor plugin makes the cursor return a python dictionary.
    conn = connection_pool.getconn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if 'DROP' in sql_stmt.upper():
        return "Permission denied. DROP commands are not supported."
    cursor.execute(sql_stmt)
    colnames = [desc[0] for desc in cursor.description]

    if 'INSERT' in sql_stmt.upper() or "UPDATE" in sql_stmt.upper():
        conn.commit()
        cursor.close()
        return
    data = cursor.fetchall()
    cursor.close()
    if col_names:
        return data, colnames
    return data


class CSVForm(FlaskForm):
    """Defines a CSV upload form"""
    table = SelectField('table', choices=[('Tests', 'tests'), ('Results', 'results')])
    csvfile = FileField('CSV File', validators=[FileRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
    title = "CSV Upload Form"
    form = CSVForm()
    if request.method == 'POST':
        file_data = request.files[form.csvfile.name].read().decode('ascii', 'ignore').strip()
        mydict = [
            {k: v for k, v in row.items()}
            for row in
            csv.DictReader(file_data.splitlines(), skipinitialspace=True)]
        table = form.table.data
        col_names = (get_db_columns(table=table))
        errors = validate_columns(mydict, col_names)
        valid = f"Valid Columns:{col_names}"
        if errors:
            return render_template('422.html', error=errors, valid=valid)

        return jsonify(mydict)
    return render_template('csv.html', title=title, form=form)

def validate_columns(data, colnames):
    errors = []
    num = 1
    for entry in data:
        for key in entry.keys():
            if key not in colnames:
                errormsg = (f"ERROR - Entry:{num} Column:{key} is not a valid column for the "
                            f"selected table")
                errors.append(errormsg)
        num += 1
    return errors


def get_db_columns(table):
    """
    Retrieve database columns for a given table

    :param table: Table name to retrieve
    """
    response, col_names = cur(f"Select * from {table} limit 0", col_names=True)
    return col_names

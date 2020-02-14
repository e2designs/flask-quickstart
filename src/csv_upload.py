import os
import csv
from wtforms import FileField, SelectField
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from flask import Flask, request, render_template, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

bootstrap = Bootstrap()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
app.config['UPLOADED_FOLDER'] = '/tmp/uploads'
bootstrap.init_app(app)

class CSVForm(FlaskForm):
    """Defines a CSV upload form"""
    table = SelectField('table', choices=[('Tests', 'tests'), ('Results', 'results')])
    csvfile = FileField('CSV File', validators=[FileRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
    title = "CSV Upload Form"
    form = CSVForm()
    if request.method == 'POST':
        file_data = request.files[form.csvfile.name].read().decode('utf8')
        mydict = [
            {k: v for k, v in row.items()}
            for row in
            csv.DictReader(file_data.splitlines(), skipinitialspace=True)]

        return jsonify(mydict)
    return render_template('csv.html', title=title, form=form)

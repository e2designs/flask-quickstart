from flask_wtf import FlaskForm

class BenchForm(FlaskForm):
    """Defines bench entry form"""
    name = IntegerField('Enter Bench number')
    bench_type = StringField('Enter Bench type')
    submit = SubmitField('Submit')


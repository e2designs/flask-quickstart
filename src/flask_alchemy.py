""" Example POC of flask with SQL alchemy"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://0.0.0.0:5444/mydb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tests(db.Model):
    __tablename__ = "tests"
    id = db.Column(db.Integer, primary_key=True)
    testid = db.Column(db.String(64), unique=True)
    matlvl = db.Column(db.Integer, unique=False)

    def __repr__(self):
        return f"<Tests: {self.__dict__}>"

class Results(db.Model):
    __tablename__ = "results"
    __table_args__ = (
        db.CheckConstraint("defect ~ '^D-\d{5}$|^N/A$'", name='valid_defect'),
        db.CheckConstraint("(not result ~ 'FAIL|BLOCKED') or (defect ~ '^D-\d{5}$')",
                           name="defect_id_if_fail")
    )
    id = db.Column(db.Integer, primary_key=True)
    testid = db.Column(db.String(64), db.ForeignKey('tests.testid'))
    result = db.Column(db.String(64), db.ForeignKey('result_keys.id'))
    tester = db.Column(db.String(64), db.ForeignKey('testers.id'))
    build = db.Column(db.String(64), db.ForeignKey('build.build'))
    defect = db.Column(db.String(64), server_default='N/A')
    db.relationship('Tests', backref="testid", lazy=True, uselist=False)
    db.relationship('Testers', backref="tester", lazy=True, uselist=False)
    db.relationship('Build', backref="build", lazy=True, uselist=False)
    db.relationship('Result_keys', backref="result", lazy=True, uselist=False)

    def __repr__(self):
        return f"<Results: {self.__dict__}>"

class Testers(db.Model):
    __tablename__ = "testers"
    id = db.Column(db.String(64), primary_key=True, index=True)

    def __repr__(self):
        return f"<Testers: {self.__dict__}>"

class Result_keys(db.Model):
    __tablename__ = "result_keys"
    id = db.Column(db.String(64), primary_key=True, index=True)

    def __repr__(self):
        return f"<Result_keys: {self.__dict__}>"

class Build(db.Model):
    __tablename__ = "build"
    id = db.Column(db.Integer, primary_key=True)
    build = db.Column(db.String(64), unique=True, index=True)
    build_type = db.Column(db.String(64), server_default="interm")

    def __repr__(self):
        return f"<Build: {self.__dict__}>"



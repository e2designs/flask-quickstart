import flask_alchemy as fa
from sqlalchemy.exc import IntegrityError
import logging


def log():
    logger = logging.Logger(name='init_db', level='INFO')
    ch = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt=fmt)
    logger.addHandler(ch)
    return logger


def db_init(logger):
    db = fa.db
    logger.info("Drop all existing tables to clear them out.")
    db.drop_all()
    logger.info("Create tables based on SQLAlchemy Models")
    db.create_all()
    return db


class DBCALL:

    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def insert_record(self, record):
        try:
            self.db.session.add(record)
            self.db.session.commit()
            self.logger.info(f"Record successfully inserted Record ID: {record.id}")
        except IntegrityError as sqlerr:
            fmt_msg = str(sqlerr.orig).split('\n')
            self.logger.error(f"Unable to insert record: {record}")
            [self.logger.error(f"{msg}") for msg in fmt_msg]
            self.logger.debug(f"Full exception:\n{sqlerr}")
            self.db.session.rollback()


def main():
    logger = log()
    db = db_init(logger)
    dbcall = DBCALL(db, logger)
    logger.info("Create result to enter")
    result1 = fa.Results(testid="test1", result="PASS", tester="ME", build="1234")

    logger.info(f"This entry should fail as the testid: {result1.testid} is not in the tests table")
    logger.info(f"result1.id should not return an id as it was not set:{result1.id}")
    dbcall.insert_record(result1)

    logger.info("Now update tests table with the testid entry.")

    test1 = fa.Tests(testid='test1', matlvl=7)
    dbcall.insert_record(test1)

    logger.info("Try to insert the result record again.")
    logger.info("This will fail as the build number is not in the build table")
    dbcall.insert_record(result1)

    logger.info("Insert build into build table")
    build1 = fa.Build(build='1234')
    dbcall.insert_record(build1)

    logger.info("Try to insert the result record again.")
    logger.info("This will fail as the result (verdict) is not in the result_keys table")
    dbcall.insert_record(result1)

    logger.info("Insert verdicts into the result_keys table")
    for key in ["PASS", "FAIL", "NOT_RUN", "BLOCKED"]:
        res_key = fa.Result_keys(id=key)
        dbcall.insert_record(res_key)

    logger.info("Try to insert the result record again.")
    logger.info("This will fail as the tester is not in the testers table")
    dbcall.insert_record(result1)

    logger.info("Insert tester into the testers table")
    me = fa.Testers(id='ME')
    dbcall.insert_record(me)

    logger.info("The result insert should now pass")
    dbcall.insert_record(result1)

    logger.info("Create a new result with FAIL")
    result2 = fa.Results(testid="test1", result="FAIL", tester="ME", build="1234")

    logger.info("Insert should fail as defect cannot be None")
    dbcall.insert_record(result2)

    logger.info("Update record defect to an invalid entry")
    result2.defect = "D-1234"
    dbcall.insert_record(result2)

    logger.info("Update record defect to a valid entry")
    result2.defect = 'D-12345'
    dbcall.insert_record(result2)

    logger.info("Query Entries")
    logger.info(f"TESTERS:{fa.Testers.query.all()}")
    logger.info(f"TESTS:{fa.Tests.query.all()}")
    logger.info(f"BUILD:{fa.Build.query.all()}")
    [logger.info(f"Result_keys:{result}") for result in fa.Result_keys.query.all()]
    [logger.info(f"Results:{result}") for result in fa.Results.query.all()]

if __name__ == '__main__':
    main()

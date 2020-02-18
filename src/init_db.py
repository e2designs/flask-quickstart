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

def insert_record(record, db, logger):
    try:
        db.session.add(record)
        db.session.commit()
        logger.info(f"Record successfully inserted Record ID: {record.id}")
    except IntegrityError as sqlerr:
        fmt_msg = str(sqlerr.orig).split('\n')
        logger.error(f"Unable to insert record: {record}")
        [logger.error(f"{msg}") for msg in fmt_msg]
        logger.debug(f"Full exception:\n{sqlerr}")
        db.session.rollback()

def main():
    logger = log()
    db = db_init(logger)
    logger.info("Create result to enter")
    result1 = fa.Results(testid="test1", result="PASS", tester="ME", build="1234")

    logger.info(f"This entry should fail as the testid: {result1.testid} is not in the tests table")
    logger.info(f"result1.id should not return an id as it was not set:{result1.id}")
    insert_record(result1, db, logger)

    logger.info("Now update tests table with the testid entry.")

    test1 = fa.Tests(testid='test1', matlvl=7)
    insert_record(test1, db, logger)

    logger.info("Try to insert the result record again.")
    logger.info("This will fail as the build number is not in the build table")
    insert_record(result1, db, logger)

    logger.info("Insert build into build table")
    build1 = fa.Build(build='1234')
    insert_record(build1, db, logger)

    logger.info("Try to insert the result record again.")
    logger.info("This will fail as the result (verdict) is not in the result_keys table")
    insert_record(result1, db, logger)

    logger.info("Insert verdicts into the result_keys table")
    for key in ["PASS", "FAIL", "NOT_RUN", "BLOCKED"]:
        res_key = fa.Result_keys(id=key)
        insert_record(res_key, db, logger)

    logger.info("Try to insert the result record again.")
    logger.info("This will fail as the tester is not in the testers table")
    insert_record(result1, db, logger)

    logger.info("Insert tester into the testers table")
    me = fa.Testers(id='ME')
    insert_record(me, db, logger)

    logger.info("The result insert should now pass")
    insert_record(result1, db, logger)

if __name__ == '__main__':
    main()

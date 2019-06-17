import sqlite3

def dict_factory(cur, row):
    """Creates a dictionary response for a sqlite connection

    :param cur: Database cursor
    :param row: row to examine.
    """

    d = {}
    for idx, col in enumerate(cur.description):
        d[col[0]] = row[idx]
    return d

class local_db():
    """ Class for a local memory based database """

    def __init__(self):
        """
        Creates a local in memory sqlite3 database.
        Entries are not persistent.
        """
        self.con = sqlite3.connect("my_app.db", check_same_thread=False)
        #self.con = sqlite3.connect(":memory:", check_same_thread=False)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
        #self.cur.execute("CREATE TABLE bench(name text, bench_type text, eth1 text)")
        self.con.commit()

    def __del__(self):
        """Closes the database connection"""
        self.con.close()

    def local_cur(self, cmd):
        """
        Database cursor for initialization and verification checks

        :param cmd: Command to issue to the database
        :returns data: Dictionary response from the database

        """
        self.cur.execute(cmd)
        if 'INSERT' in cmd:
            self.con.commit()
        response = self.cur.fetchall()
        return response


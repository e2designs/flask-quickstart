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
        # Example of in memory sqlite db
        #self.con = sqlite3.connect(":memory:", check_same_thread=False)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self, name=None, columns=None):
        """
        Creates a database table if it does not already exist

        :param name: Name of the table
        :param columns: String of column names and type
            E.g. 'name text, column2 int'

        """
        table_name = name or 'bench'
        columns = columns or 'name text, bench_type text, eth1 text'
        cmd = f"CREATE TABLE IF NOT EXISTS {table_name}({columns})"
        self.cur.execute(cmd)
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


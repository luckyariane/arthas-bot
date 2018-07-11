import sqlite3 as sqlite

class database:
    def __init__(file_name):
        self.con = sqlite.connect(file_name)
        self.cur = con.cursor()

    

if __name__ == '__main__':
    f = 'followers.db'
    d = database(f)
    sql = 'CREATE TABLE followers (name text, join 
    d.cur.execute(sql)

import sqlite3 as sqlite
from datetime import datetime
import settings

class Raid:
    def __init__(self):        
        self.conn = sqlite.connect(settings.ROOT_PATH + r'\Data\Databases\RaidDB.sqlite')
        self.cur = self.conn.cursor()

##    def delete(self):
##        sql = "DROP TABLE raid_prog"
##        self.cur.execute(sql)

    def delete2(self):
        sql = "DROP TABLE raid_events"
        self.cur.execute(sql)

##    def initialize(self):
##        sql = """CREATE TABLE
##                    IF NOT EXISTS raid_prog (
##                    id integer PRIMARY KEY,
##                    name text NOT NULL,
##                    start_date text,
##                    wipes integer,
##                    clears integer,
##                    prog integer,
##                    clear_date text,
##                    wipes_til_clear integer,
##                    current boolean,
##                    UNIQUE(name)
##                    )"""
##        self.cur.execute(sql)

    def init2(self):
        sql = """CREATE TABLE
                    IF NOT EXISTS raid_events (
                    id integer PRIMARY KEY,
                    boss text NOT NULL,
                    timestamp text,
                    type text,
                    prog integer,
                    valid boolean,
                    UNIQUE (boss, timestamp, type) ON CONFLICT Ignore
                    )"""
        self.cur.execute(sql)

    def dbDump(self):
##        sql = "SELECT * FROM raid_prog"
##        self.cur.execute(sql)
##
##        dump = ""
##        for id, name, start_date, wipes, clears, prog, clear_date, wipes_til_clear, current in self.cur.fetchall():
##            dump += '#' * 20
##            dump += '\nBoss: %s\n' % name
##            dump += 'First Attempt on %s [%s]\n' % (self.formatDate(start_date), start_date)
##            dump += 'Total Wipes: %s\n' % wipes
##            dump += 'Total Clears: %s\n' % clears
##            dump += 'Best Progresson: ' + str(prog) + '%'
##            if clear_date:
##                dump += '\nFirst Cleared: %s [%s]\n' % (self.formatDate(clear_date), clear_date)
##                dump += 'Number of Wipes before First Clear: %s\n' % wipes_til_clear
##            else:
##                dump += '\nFirst Cleared: IN PROGRESS\n'
##                dump += 'Number of Wipes before First Clear: IN PROGRESS\n'
##            if current == 1:
##                dump += 'Boss is Current\n'
##            else:
##                dump += 'Boss data is retired\n'
##            dump += '#' * 20
##            dump += '\n' * 3
##
##        print dump

        sql2 = "SELECT * from raid_events"
        self.cur.execute(sql2)

        for id, boss, stamp, event_type, prog, valid in self.cur.fetchall():
            print id, boss, stamp, event_type, prog, valid

        fn = 'raid_prog_db_' + datetime.today().strftime('-%b%d-%Y-%f').lower()

        with open('G:\Stream\Data\Databases\Logs\%s.txt' % fn, 'w') as f:
            f.write(dump)
            f.close()
            
    def addBoss(self, boss):
        sql = "INSERT OR IGNORE INTO raid_prog(name, start_date, wipes, clears, prog, current) VALUES(?, ?, 0, 0, 100, 1)"
        self.cur.execute(sql, (boss, datetime.today()))
        self.conn.commit()

    def getBoss(self, boss):
        sql = "SELECT name, wipes, clears, prog FROM raid_prog WHERE name=?"
        self.cur.execute(sql, (boss,))
        return self.cur.fetchone()

    def setWipes(self, boss, count):
        sql = "UPDATE raid_prog SET wipes=? WHERE name=?"
        self.cur.execute(sql, (count, boss))
        self.conn.commit()

    def setClears(self, boss, count, wipes):
        if count == 0:
            sql = "UPDATE raid_prog SET clears=?, clear_date=NULL, wipes_til_clear=0 WHERE name=?"
        elif count == 1:
            self.setWin(boss, wipes)
            return
        else:
            sql = "UPDATE raid_prog SET clears=? WHERE name=?"
        self.cur.execute(sql, (count, boss))
        self.conn.commit()

    def setProg(self, boss, val):
        sql = "UPDATE raid_prog SET prog=? WHERE name=?"
        self.cur.execute(sql, (val, boss))
        self.conn.commit()

    def setWin(self, boss, wipe_count):
        sql = "UPDATE raid_prog SET clears=1, clear_date=?, wipes_til_clear=? WHERE name=?"
        self.cur.execute(sql, (datetime.today(), wipe_count, boss))
        self.conn.commit()

    def storeEvent(self, boss, event_type, ts, prog=None):
        if prog:
            sql = "INSERT INTO raid_events(boss, timestamp, type, prog, valid) VALUES(?, ?, ?, ?, 1)"
            self.cur.execute(sql, (boss, ts, event_type, prog))
        else:
            sql = "INSERT INTO raid_events(boss, timestamp, type, valid) VALUES(?, ?, ?, 1)"
            self.cur.execute(sql, (boss, ts, event_type))
        self.conn.commit()

    def getBosses(self):
        #sql = "SELECT name FROM raid_prog WHERE current=1"
        sql = "SELECT boss FROM raid_events"
        self.cur.execute(sql)
        print self.cur.fetchall()
        return sorted([str(x[0]) for x in self.cur.fetchall()])

    def retireBoss(self, boss):
        sql = "UPDATE raid_prog SET current=0 WHERE name=?"
        self.cur.execute(sql, (boss,))
        self.conn.commit()

    def unRetireBoss(self, boss):
        sql = "UPDATE raid_prog SET current=1 WHERE name=?"
        self.cur.execute(sql, (boss,))
        self.conn.commit()

    def formatDate(self, date):
        d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        return d.strftime('%B %d, %Y', )

    def temp(self):
        sql = "UPDATE raid_prog SET wipes_til_clear=73 WHERE name='Susano'"
        self.cur.execute(sql)
        self.conn.commit()



if __name__ == '__main__':
    raid = Raid()
    #raid.delete2()
    #raid.init2()
    #raid.unRetireBoss('TestBoss')
    #raid.delete()
    #raid.initialize()
    #raid.addBoss('Exdeath')
    #print raid.getBoss('O1S')
    #print raid.getBosses()
    #raid.retireBoss('TestBoss')
    #raid.temp()
    #raid.setClears('Susano', 73, 98)
    raid.dbDump()

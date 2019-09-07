from settings import ROOT_PATH
from utils import get_webpage, convert_json, add_points_multi
import sqlite3 as sqlite 
from datetime import datetime, timedelta

class LoyaltyPoints():    
    def __init__(self):     
        self.lastRun = datetime.now()
        self.delay = 300 # in seconds
        self.increment = 1 # per delay
        
        # track users
        self.url = 'https://tmi.twitch.tv/group/user/luckyariane/chatters'
        self.current_users = list()   

        # database
        self.con = sqlite.connect(ROOT_PATH + r'\Data\Databases\currency.db')
        self.cur = self.con.cursor()
        self.__initDB()

    def checkCurrency(self):
        d = datetime.now() - self.lastRun
        if d.seconds < self.delay:
            return 

        self.getCurrentUsers()
        self.incrementCurrency()
        self.lastRun = datetime.now()

    def getCurrentUsers(self):
        self.current_users = list()        
        api_dict = convert_json(get_webpage(self.url))
        for user_type in api_dict['chatters']:
            self.current_users += api_dict['chatters'][user_type]

    def incrementCurrency(self):
        sql = 'SELECT user FROM currency WHERE user in ({seq})'.format(seq=','.join(['?'] * len(self.current_users)))
        self.cur.execute(sql, tuple(self.current_users))
        db_user_list = [str(x) for x, in self.cur.fetchall()]
        for user in self.current_users:
            if user not in db_user_list:
                sql = 'INSERT INTO currency(user, timestamp, amount) VALUES(?, ?, ?)'
                self.cur.execute(sql, (user, datetime.now(), self.increment))
        add_points_multi(self, self.current_users, self.increment)
        self.con.commit()

    def dump(self):
        sql = 'SELECT * FROM currency'
        self.cur.execute(sql)
        for data in self.cur.fetchall():
            print data

    def __initDB(self):        
        sql = """CREATE TABLE
                    IF NOT EXISTS currency (
                    id integer PRIMARY KEY,
                    user text NOT NULL,
                    timestamp text,
                    amount integer,
                    UNIQUE (user) ON CONFLICT Ignore
                    )"""
        self.cur.execute(sql)
        self.con.commit()

if __name__ == '__main__':
    c = LoyaltyPoints()
    #c.checkCurrency()
    #c.dump()
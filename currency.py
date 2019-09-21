import sqlite3 as sqlite 
from settings import ROOT_PATH
from utils import get_webpage, convert_json, add_points_multi
from cooldowns import set_cooldown, on_cooldown, get_timestamp, five_mins

class LoyaltyPoints():    
    def __init__(self):     
        self.lastRun = set_cooldown()
        self.delay = five_mins
        self.increment = 1 # per delay
        
        # track users
        self.url = 'https://tmi.twitch.tv/group/user/luckyariane/chatters'
        self.current_users = list()   

        # database
        self.con = sqlite.connect(ROOT_PATH + r'\Data\Databases\currency.db')
        self.cur = self.con.cursor()
        self.__initDB()

    def checkCurrency(self):
        if on_cooldown(self.lastRun, self.delay):
            return 

        self.getCurrentUsers()
        self.incrementCurrency()
        self.lastRun = set_cooldown()

    def getCurrentUsers(self):
        self.current_users = list()        
        api_dict = convert_json(get_webpage(self.url))
        for user_type in api_dict['chatters']:
            self.current_users += api_dict['chatters'][user_type]

    def incrementCurrency(self):
        add_points_multi(self, self.current_users, self.increment, time_tracking=True)
        self.con.commit()

    def dump(self):
        sql = 'SELECT * FROM currency'
        self.cur.execute(sql)
        for data in self.cur.fetchall():
            print data

    def fixCurrency(self, user, amount):
        sql = 'UPDATE currency SET amount = ? WHERE user = ?'
        self.cur.execute(sql, (amount, user))
        self.con.commit()

    def __initDB(self):        
        sql = """CREATE TABLE
                    IF NOT EXISTS currency (
                    id integer PRIMARY KEY,
                    user text NOT NULL,
                    timestamp text,
                    amount integer,
                    time_increments integer,
                    UNIQUE (user) ON CONFLICT Ignore
                    )"""
        self.cur.execute(sql)
        self.con.commit()

if __name__ == '__main__':
    c = LoyaltyPoints()
    #c.checkCurrency()
    c.dump()
import os, time, re
import sqlite3 as sqlite
#from datetime import datetime
import utils
import settings

#for multi-boss fights
BOSS_MAP = {
    #'Exdeath' : 'Neo Exdeath',
    #'Twintania' : 'Nael deus Darnus',
    }

INV_BOSS_MAP = {
    'Nael deus Darnus' : 'Twintania',
    'Bahamut Prime' : 'Twintania',
    }

class RaidData():
    def __init__(self):        
        self.conn = sqlite.connect(settings.ROOT_PATH + r'\Data\Databases\RaidDB.sqlite')
        self.cur = self.conn.cursor()
        self.dir = settings.ROOT_PATH + r'\Data'
        
    def delete(self):
        sql = "DROP TABLE raid_events"
        self.cur.execute(sql)
        self.conn.commit()
        
    def init(self):
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
        self.conn.commit()
        
        
    def dump(self):

        sql2 = "SELECT * from raid_events"
        self.cur.execute(sql2)

        for id, boss, stamp, event_type, prog, valid in self.cur.fetchall():
            print id, boss, stamp, event_type, prog, valid
            
    def storeEvent(self, boss, event_type, ts, prog):
        sql = "INSERT INTO raid_events(boss, timestamp, type, prog, valid) VALUES(?, ?, ?, ?, 1)"
        self.cur.execute(sql, (boss, ts, event_type, prog))
        self.conn.commit()
        self.updateStreamView(boss)
        
    def getBosses(self):
        sql = "SELECT boss FROM raid_events"
        self.cur.execute(sql)
        print self.cur.fetchall()
        return sorted([str(x[0]) for x in self.cur.fetchall()])
        
    def updateStreamView(self, boss):
        if boss in BOSS_MAP:
            boss = BOSS_MAP[boss]
        
        utils.update_file(r'%s\cur_boss.txt' % self.dir, boss)
        
        sql = "SELECT timestamp FROM raid_events WHERE boss=? AND type='WIPE'"
        self.cur.execute(sql, (boss,))
        utils.update_file(r'%s\\boss_wipe.txt' % self.dir, len(self.cur.fetchall()))
        
        sql = "SELECT timestamp FROM raid_events WHERE boss=? AND type='WIN'"
        self.cur.execute(sql, (boss,))
        utils.update_file(r'%s\\boss_kill.txt' % self.dir, len(self.cur.fetchall()))
        
        sql = "SELECT min(prog) FROM raid_events WHERE boss=?"
        self.cur.execute(sql, (boss,))
        utils.update_file(r'%s\\boss_prog.txt' % self.dir, str(self.cur.fetchone()[0]) + '%')
        
    def viewData(self, boss):
        sql = "SELECT * FROM raid_events WHERE boss=?"
        self.cur.execute(sql, (boss,))
        for data in self.cur.fetchall():
            print data
            
    def addMissingData(self, boss, type, count):
        if type == 'WIPE': prog = 100
        elif type == 'WIN': prog = 0
        sql = "INSERT INTO raid_events (boss, timestamp, type, prog, valid) VALUES(?, ?, ?, ?, 1)"
        for i in range(1, count + 1):
            self.cur.execute(sql, (boss, i, type, prog))
        self.conn.commit()

    def queryStats(self, boss):
        stats = dict()
        sql = "SELECT * FROM raid_events WHERE boss=?"
        self.cur.execute(sql, (boss,))
        for id, boss, timestamp, type, percent, valid in self.cur.fetchall():
            date = time.strptime(timestamp.split('.')[0], '%Y-%m-%dT%H:%M:%S')
            if date.tm_hour < 12:
                d = date.tm_mday - 1
            else: d = date.tm_mday
            day = (date.tm_mon, d)
            if day not in stats:
                stats[day] = dict()
                stats[day]['pulls'] = 0
                stats[day]['wipes'] = 0
                stats[day]['wins'] = 0
            if type == 'WIN':
                stats[day]['wins'] += 1
            elif type == 'WIPE':
                stats[day]['wipes'] += 1
            stats[day]['pulls'] += 1

        for day in sorted(stats.keys()):
            print '%s\t\tP:%s N:%s P:%s' % (day, stats[day]['pulls'], stats[day]['wins'], stats[day]['wipes'])
                
        


class RaidParse():
    def __init__(self):
        self.PERCENT = 100
        self.BOSS = None
        self.rd = RaidData()
        self.trackedBosses = self.getCurBosses()
        self.parse = False
        self.zone = None

    def getCurBosses(self):
        with open(settings.ROOT_PATH + r'\Data\tracked_bosses.txt', 'r') as f:
            bosses = f.read().split('\n')
            f.close()
        return bosses

    def getLogFiles(self, path, n):
        files = [path + x for x in os.listdir(path)]
        if n:
            return sorted(files)[-n:]
        else:
            return sorted([x for x in files if 'Network' in x])
        
##        date = datetime.today()
##        filename = 'Network_%s%02d%02d.log' % (date.year, date.month, date.day)
##        path = 'D:\ACT Logs\\' + filename
##
##        if not os.path.isfile(path):
##            filename = 'Network_%s%02d%s.log' % (date.year, date.month, date.day - 1)
##            path = 'D:\ACT Logs\\' + filename

##        return path
                    
    def healthPercent(self, x, y):
        return int((float(x) / float(y)) * 100)

    def parseAttack(self, line):
        #type_code = line[0]
        #timestamp = line[1]
        #attacker_code = line[2]
        #attacker_name = line[3]
        #attack_code = line[4]
        #attack_name = line[5]
        #attacked_code = line[6]
        attacked_name = line[7]
        #a = line[8:23]
        attacked_current_health = line[24]
        attacked_max_health = line[25]
    ##    attacked_current_mana = line[26]
    ##    attacked_max_mana = line[27]
    ##    attacked_current_tp = line[28]
    ##    attacked_max_tp = line[29]
    ##    attacked_coordiantes = line[30:32]
    ##    #b = line[32]    
    ##    attacker_current_health = line[33]
    ##    attacker_max_health = line[34]
    ##    attacker_current_mana = line[35]
    ##    attacker_max_mana = line[36]
    ##    attacker_current_tp = line[37]
    ##    attacker_max_tp = line[38]
    ##    attacker_coordiantes = line[39:41]
    ##    #c = line[41]
    ##    hash_code = line[42]

        if attacked_name == self.BOSS:
            self.PERCENT = self.healthPercent(attacked_current_health, attacked_max_health)
            
    def parseDeath(self, line):
        #type_code = line[0]
        timestamp = line[1]
        #killed_code = line[2]
        killed_name = line[3]
        #killer_code = line[4]
        killer_name = line[5]
        #a = line[6]
        #hash_code = line[7]
        #print '%s | %s' % (killed_name, killed_name == self.BOSS)
        if killed_name == self.BOSS:
            self.rd.storeEvent(self.BOSS, 'WIN', timestamp, 0)
            print 'DEAD: %s (%s)' % (self.BOSS, timestamp)
            self.PERCENT = 100

    def nonDeathPhasePush(self, new_boss, timestamp, health):
        self.rd.storeEvent(self.BOSS, 'WIN', timestamp, health)
        print 'DEAD: %s (%s)' % (self.BOSS, timestamp)
        self.reset()
        self.BOSS = new_boss

    def parseLoad(self, data):
        if data[7] != '0':
            if self.PERCENT != 100:
                self.rd.storeEvent(self.BOSS, 'WIPE', data[1], self.PERCENT)
                print 'WIPE [%s] (%s): %s' % (self.PERCENT, data[1], self.BOSS)
                self.PERCENT = 100
                if self.BOSS in INV_BOSS_MAP:
                    self.BOSS = INV_BOSS_MAP[self.BOSS]

    def parseForBoss(self, line):
        for boss in self.trackedBosses:
            if boss in line:
                self.BOSS = boss
                print 'Setting Boss: %s' % self.BOSS
                self.rd.updateStreamView(self.BOSS)
                break
                
    def parseZone(self, line):
        zone = line.split('|')[4]
        for zoneType in ['Extreme', 'Savage', 'Minstrel\'s Ballad', 'Ultimate']:
            if zoneType in zone:
                self.parse = True
                self.zone = zone.replace(' has begun.', '')
                print 'Found Parsable Zone: %s' % self.zone
                break
        else:
            self.parse = False
        print self.parse

    def parseLine(self, line):        
        split_line = line.split('|')
        data_type = split_line[0]
        if data_type == '01': self.reset()
        if not self.BOSS and not data_type == '03':
            return
        elif not self.BOSS:
            self.parseForBoss(line)
            return
        if data_type == '00' and ' has begun' in line: self.parseZone(line)
        if self.parse:
            if self.BOSS in line:
                if data_type == '03': self.parseLoad(split_line)
                #if data_type == '04': self.parseUnload(split_line)
                if data_type == '21': self.parseAttack(split_line)
                if data_type == '25': self.parseDeath(split_line)
                
            ####Special Cases####
            if self.BOSS == 'Exdeath' and data_type == '00' and 'I am Neo Exdeath.' in line:
                self.nonDeathPhasePush('Neo Exdeath', split_line[1], 59)
##                self.rd.storeEvent(self.BOSS, 'WIN', split_line[1], 59)
##                print 'DEAD: %s (%s)' % (self.BOSS, split_line[1])
##                self.reset()
##                self.BOSS = 'Neo Exdeath'
            if self.BOSS == 'Twintania' and data_type == '22' and split_line[3] == 'Ragnarok': 
                self.nonDeathPhasePush('Nael deus Darnus', split_line[1], 0)

    def reset(self):
        self.BOSS = None
        self.PERCENT = 100

    def readFullLog(self, path): #read existing logs
        with open(path, 'rb+') as f:
            while True:
                line = f.readline()
                self.parseLine(line)
                if line == '': break
        return

    def readCurLog(self, path): #read new log
        with open(path, 'rb+') as f:
            #f.seek(-100, 2)
            while True:
                line = f.readline()
                if line.strip() == '':
                    time.sleep(5)
                    continue
                #print line
                if '\n' not in line:
                    f.seek(len(line) * -1, 2)
                    time.sleep(5)
                    continue                
                self.parseLine(line)

    def main(self, path, n=2):
        files = self.getLogFiles(path, n)
        latest = files[-1]
        for f in files:
            if f == latest:
                self.readCurLog(f)
                #self.readFullLog(f)
            else:
                self.readFullLog(f)


if __name__ == '__main__':
    rp = RaidParse()
    #rp.rd.delete()
    #rp.rd.init()
    #rp.rd.addMissingData('Susano', 'WIPE', 83)
    #rp.rd.addMissingData('Susano', 'WIN', 25)
    #rp.rd.addMissingData('Lakshmi', 'WIPE', 14)
    #rp.rd.addMissingData('Lakshmi', 'WIN', 17)
    #rp.rd.viewData('Susano')
    #sys.exit(1)
    rp.main(r'G:\ACT Logs\', None)
    #rp.rd.dump()
    #rp.rd.viewData('Twintania')
    #rp.rd.updateStreamView('Twintania')
    #rp.rd.queryStats('Nael deus Darnus')

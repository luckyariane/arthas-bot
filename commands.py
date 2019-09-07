from datetime import datetime, timedelta
import sqlite3 as sqlite
import random_command
import chocobo_racing
import utils
import raid_db
import random
import settings

class Commands():
    def __init__(self, con, cur): 
        # constants
        self.currency_name = 'clovers'

        # support objects
        self.con = con
        self.cur = cur

        self.dir = settings.ROOT_PATH
        self.regulars = settings.REGULARS
        self.moderators = settings.MODERATORS
        self.admin = [settings.CHANNEL_NAME]
        self.user = None
        self.recent_chatters = list()
        self.prizes = ['MINION'] * 19 + ['OUTFIT'] * 2 + ['MOUNT']
        self.winners = []

        #all commands and their functions
        self.commands_public = {
            '!%s' % self.currency_name : self.command_currency,
            '!win': self.command_kill,
            '!wipe': self.command_wipe,
            '!bet': self.command_bet,
            '!random': self.command_random,
            '!beg' : self.command_beg,
            '!scrub' : self.command_scrub,
            '!nextstream' : self.command_nextstream,
            '!not8th': self.command_not8th,
            '!bonus': self.command_bonus,
            #'!race' : self.command_race,
            #'!merrychristmas' : self.command_merrychristmas,
        }
        self.commands_regulars = {
            #'!curboss': self.command_curboss,
            #'!bossquery': self.command_bossquery,
            #'!betstart': self.command_betstart,
            #'!betclose': self.command_betclose,
        }
        self.commands_moderators = {
            '!addreg': self.command_addreg,
            #'!betpay': self.command_betpay,
            #'!betopts': self.command_betopts,
            #'!raidstart' : self.command_raidstart,
            #'!raidstop' : self.command_raidstop,
            # '!createboss': self.command_createboss,
        }
        self.commands_private = {
            '!addmod': self.command_addmod,
        }

        self.init_time = datetime.now() - timedelta(seconds=50000)
        self.cooldowns = {
            '!betpay'   : self.init_time,
            '!win'      : self.init_time,
            '!wipe'     : self.init_time,
            '!unwipe'   : self.init_time,
            '!race'     : self.init_time,
        }

        # functionality for !race
        self.entry_open = False

        #functionality for betting
        self.start_bet = False
        self.bets = dict()
        self.betters = list()
        self.bet_options = dict()

    #basic functions declared below
    # --------------------------------------------- Start Command Functions --------------------------------------------

    def command_currency(self, data):
        return '%s you have %i %s' % (self.user, utils.get_points(self, self.user), self.currency_name)

    # def command_createboss(self, data):
    #     new_cur_boss = ' '.join(data[1:]).strip()
        
    #     if len(new_cur_boss) != 0:
    #         self.raidDb.addBoss(new_cur_boss)
    #         return 'Created: %s' % new_cur_boss

    def command_kill(self, data):
        gil = 1
        d = datetime.now() - self.cooldowns['!win']
        if d.seconds > 60:
            gil = 10
            self.cooldowns['!win'] = datetime.now()
        if utils.add_points(self, self.user, gil):
            return 'Thanks %s! Have %s %s!' % (self.user, gil, self.currency_name)
        else:
            return 'Thanks %s!' % self.user

    def command_wipe(self, data):
        gil = 1
        d = datetime.now() - self.cooldowns['!wipe']
        if d.seconds > 60:
            gil = 10
            self.cooldowns['!wipe'] = datetime.now()
        if utils.add_points(self, self.user, gil):
            return 'Thanks %s! Have %s %s!' % (self.user, self.currency_name)
        else:
            return 'Thanks %s!' % self.user

    def command_addreg(self, data):
        self.regulars.append(data)

    def command_addmod(self, data):
        self.moderators.append(data)

    def command_betstart(self, data):
        self.start_bet = True
        self.bets = dict()
        self.betters = list()
        self.bet_options = dict()
        return 'Betting has started.  Enter with !bet <value>'

    def command_betclose(self, data):
        if self.start_bet == False:
            return True
        self.start_bet = False
        print '=' * 20
        print 'BETS ENTERED:'
        for key in sorted(self.bet_options):
            print '    %s (%s): %s' % (key, self.bet_options[key]['option'], ', '.join(self.bet_options[key]['users']))
        print '=' * 20
        return 'Betting now closed.  Betters are: %s' % ', '.join(self.betters)

    def command_bet(self, data):
        if not self.start_bet:
            return True
        if self.user in self.betters:
            return True
        option = ' '.join(data[1:]).lower().strip()
        if len(option) == 0:
            return True
        if option not in self.bets:
            self.bets[option] = list()
        self.bets[option].append(self.user)
        self.betters.append(self.user)
        self.update_bet_options()
        return True

    def command_betpay(self, data):
        d = datetime.now() - self.cooldowns['!betpay']
        if d.seconds < 60:
            return True
        try:
            payout = int(data[1])
        except ValueError:
            return 'Incorrect payout set.  Format must be !betpay <payout #> option1 option2 etc'
        win_opts = data[2:]
        winners = list()
        for opt in win_opts:
            try:
                val = int(opt)
            except ValueError: continue
            if val in self.bet_options:
                #self.cur.execute('UPDATE CurrencyUser SET Points = Points + %s WHERE Name in ("%s")' % (payout, '","'.join(self.bet_options[val]['users'])))
                utils.add_points_multi(instance, self.bet_options[val]['users'], payout)
                winners += self.bet_options[val]['users']
        self.con.commit()
        self.cooldowns['!betpay'] = datetime.now()
        return 'Added %s %s to: %s' % (payout, self.currency_name, ', '.join(winners))

    def command_betopts(self, data):
        bet_options = ['option (value, count)']
        for key in sorted(self.bet_options):
            bet_options.append('%s (%s)' % (key, self.bet_options[key]['option']))
        return ', '.join(bet_options)

    def command_random(self, data):
        return random_command.command_random(self, data)
    
    def command_not8th(self, data):
        for better in self.betters:
            utils.add_points(self, better, 1)
        return 'Yay not 8th!  All betters get 1 %s! (%s)' % ', '.join(self.betters, self.currency_name)

    def command_bonus(self, data):
        for better in self.betters:
            utils.add_points(self, better, 5)
        return 'Yay Bonus! All betters get 5 %s! (%s)' % ', '.join(self.betters, self.currency_name)

    def command_beg(self, data):
        if utils.get_points(self, self.user) < 5:
            success = utils.add_points(self, self.user, 5)
            if success:
                return '%s tosses %s 5 %s out of pity.' % (settings.NICKNAME, self.user, self.currency_name)
        else:
            return 'Get outta here %s!  You\'re not broke!' % self.user

    def command_scrub(self, data):
        try:
            user = data[1]
        except IndexError:
            pass
        if user.strip() == '': user = settings.NICKNAME
        return "%s isn't failing, %s.  It's a strategy." % (user, self.user)
            
    def command_nextstream(self, data):
        d = datetime.now()
        curday = d.weekday()
        curhour = d.hour
        raw_schedule = utils.read_file(settings.ROOT_PATH + r'\Data\schedule.txt').strip()
        schedule = dict()
        for line in raw_schedule.split('\n'):
            line_data = line.split(',') 
            weekday_num     = int(line_data[0])
            schedule[weekday_num] = dict()
            schedule[weekday_num]['name']   = line_data[1]
            if line_data[2] == 'None':
                schedule[weekday_num]['times']  = None
            else:
                schedule[weekday_num]['times']  = line_data[2:]

        next_stream = (None, None)
        day = curday
        while next_stream[1] == None:
            if schedule[day]['times'] != None:
                for time in schedule[day]['times']:
                    if curday == day and time < curhour:
                        next_stream = (schedule[day]['name'], self.convert_24hour_time(time))
                        break
                    elif curday != day:
                        next_stream = (schedule[day]['name'], self.convert_24hour_time(time))
                        break
            day = (day + 1) % 7
        return settings.NICKNAME + "'s next stream will start %s at %sm EST" % next_stream
    
    def command_race(self, data):
        if self.entry_open == False:
            d = datetime.now() - self.cooldowns['!race']
            if d.seconds < 120:
                return "%s is trying to register for the Chocobo Racing Lucky Cup, but they forgot to train their chocobo.  Try again in %s seconds." % (instance.user, 120 - d.seconds)
            self.entry_open = True
            race = chocobo_racing.ChocoboRace()
            race.register_racer(self, data)
            return "%s has registered for the Chocobo Racing Lucky Cup. Everyone can Join! To join type !race (amount)" % self.user

        else:
            race.register_racer(self, data)

    def command_merrychristmas(self, data):
        if self.user in self.winners:
            return None
        #print self.prizes
        prize = random.choice(self.prizes)
        self.prizes.pop(self.prizes.index(prize))
        #print self.prizes
        self.winners.append(self.user)
        return 'Congratulations %s!  You have won a %s from the mog station!  Please let %s know which you would like so she can send it!' % (self.user, prize, settings.NICKNAME)
        
        
    # --------------------------------------------- End Command Functions ----------------------------------------------

    #support functions
    def get_commands_dict(self, user):
        commands = self.commands_public.copy()
        if user in self.regulars + self.moderators + self.admin:
            commands = utils.merge_dicts(commands, self.commands_regulars)
        if user in self.moderators + self.admin:
            commands = utils.merge_dicts(commands, self.commands_moderators)
        if user in self.admin:
            commands = utils.merge_dicts(commands, self.commands_private)
        return commands

    def set_user(self, user):
        self.user = user

    def update_bet_options(self):
        new_bet_options = dict()
        count = 1
        for item in sorted(self.bets):
            new_bet_options[count] = dict()
            new_bet_options[count]['option'] = item
            new_bet_options[count]['users'] = self.bets[item]
            count += 1
        self.bet_options = new_bet_options

    def convert_24hour_time(self, time):
        if int(time) > 12:
            return str(int(time) - 12) + 'p'
        elif time == 12:
            return str(time) + 'p'
        elif time == 0:
            return '12a'
        else:
            return str(time) + 'a'


        
        

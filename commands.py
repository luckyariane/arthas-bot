import sqlite3 as sqlite
import random
from random_command import command_random
# from chocobo_racing import ChocoboRace
from utils import get_points, add_points, add_points_multi, read_file, merge_dicts
from settings import ROOT_PATH, REGULARS, MODERATORS, CHANNEL_NAME, NICKNAME
from cooldowns import init_cooldown, set_cooldown, on_cooldown, get_cooldown, get_timestamp, one_min, two_mins, three_mins, five_mins

class Commands():
    def __init__(self, con, cur): 
        # constants
        self.currency_name = 'clovers'

        # db objects
        self.con = con
        self.cur = cur

        self.dir = ROOT_PATH
        self.regulars = REGULARS
        self.moderators = MODERATORS
        self.admin = [CHANNEL_NAME]
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
            # '!race' : self.command_race,
            #'!merrychristmas' : self.command_merrychristmas,
        }
        self.commands_regulars = {
            #'!curboss': self.command_curboss,
            #'!bossquery': self.command_bossquery,
            '!betstart': self.command_betstart,
            '!betclose': self.command_betclose,
        }
        self.commands_moderators = {
            '!addreg': self.command_addreg,
            '!betpay': self.command_betpay,
            '!betopts': self.command_betopts,
            '!not8th': self.command_not8th,
            '!bonus': self.command_bonus,
            '!raidstart' : self.command_raidstart,
            '!raidstop' : self.command_raidstop,
            # '!racestart' : self.command_racestart,
            # '!racestop' : self.command_racestop,
        }
        self.commands_private = {
            '!addmod': self.command_addmod,
        }

        self.cooldowns = {
            '!betpay'   : init_cooldown(),
            '!win'      : init_cooldown(),
            '!wipe'     : init_cooldown(),
            '!not8th'   : init_cooldown(),
            '!bonus'    : init_cooldown(),
            # '!race'     : init_cooldown(),
        }

        # functionality for !race
        self.entry_open = False

        # functionality for betting
        self.start_bet = False
        self.bets = dict()
        self.betters = list()
        self.bet_options = dict()
        self.bet_payout = 5

        # functionality for raiding
        self.raid = False

        # functionality for chocobo racing
        # self.racing = False

    # --------------------------------------------- Start Local Command Functions --------------------------------------------

    def command_currency(self, data):
        points = get_points(self, self.user)
        return '%s you have %i %s' % (self.user, points, self.fmt_currency_name(points))

    def command_addreg(self, data):
        self.regulars.append(data[1])
        return 'Regulars: %s' % self.regulars

    def command_addmod(self, data):
        self.moderators.append(data[1])
        return 'Moderators: %s' % self.moderators

    def command_raidstart(self, data):
        self.raid = True
        return "Raid mode enabled.  You can now gain points with !win and !wipe"

    def command_raidstop(self, data):
        self.raid = False
        return "Raid mode disabled."

    def command_kill(self, data):
        if not self.raid: return True
        gil = 1
        if not on_cooldown(self.cooldowns['!win'], one_min):
            gil = 5
            self.cooldowns['!win'] = set_cooldown()
        if add_points(self, self.user, gil):
            return 'Thanks %s! Have %s %s!' % (self.user, gil, self.fmt_currency_name(gil))
        else:
            return 'Thanks %s!' % self.user

    def command_wipe(self, data):
        if not self.raid: return True
        gil = 1
        if not on_cooldown(self.cooldowns['!wipe'], one_min):
            gil = 5
            self.cooldowns['!wipe'] = set_cooldown()
        if add_points(self, self.user, gil):
            return 'Thanks %s! Have %s %s!' % (self.user, gil, self.fmt_currency_name(gil))
        else:
            return 'Thanks %s!' % self.user

    def command_betstart(self, data):
        self.start_bet = True
        self.bets = dict()
        self.betters = list()
        self.bet_options = dict()
        self.bet_payout = data[1]
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
        if on_cooldown(self.cooldowns['!betpay'], one_min):
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
                add_points_multi(self, self.bet_options[val]['users'], payout)
                winners += self.bet_options[val]['users']
        self.con.commit()
        self.cooldowns['!betpay'] = set_cooldown()
        return 'Added %s %s to: %s' % (payout, self.currency_name, ', '.join(winners))

    def command_betopts(self, data):
        bet_options = ['option (id, value)']
        for key in sorted(self.bet_options):
            bet_options.append('%s (%s)' % (key, self.bet_options[key]['option']))
        return ', '.join(bet_options)
    
    def command_not8th(self, data):
        if on_cooldown(self.cooldowns['!not8th'], three_mins): return True
        for better in self.betters:
            add_points(self, better, 1)
        self.cooldowns['!not8th'] = set_cooldown()
        return 'Yay not 8th!  All betters get 1 %s! (%s)' % (self.fmt_currency_name(1), ', '.join(self.betters))

    def command_bonus(self, data):
        if on_cooldown(self.cooldowns['!bonus'], three_mins): return True
        for better in self.betters:
            add_points(self, better, 5)
        self.coodowns['!bonus'] = set_cooldown()
        return 'Yay Bonus! All betters get 5 %s! (%s)' % (self.fmt_currency_name(5), ', '.join(self.betters))

    def command_beg(self, data):
        if get_points(self, self.user) < 5:
            success = add_points(self, self.user, 5)
            if success:
                return '%s tosses %s 5 %s out of pity.' % (NICKNAME, self.user, self.currency_name)
        else:
            return 'Get outta here %s!  You\'re not broke!' % self.user

    def command_scrub(self, data):
        try:
            user = data[1]
        except IndexError:
            pass
        if user.strip() == '': user = NICKNAME
        return "%s isn't failing, %s.  It's a strategy." % (user, self.user)
            
    def command_nextstream(self, data):
        d = get_timestamp()
        curday = d.weekday()
        curhour = d.hour
        raw_schedule = read_file(ROOT_PATH + r'\Data\schedule.txt').strip()
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
                    if curday == day and time > curhour:
                        next_stream = (schedule[day]['name'], self.convert_24hour_time(time))
                        break
                    elif curday != day:
                        next_stream = (schedule[day]['name'], self.convert_24hour_time(time))
                        break
            day = (day + 1) % 7
        return NICKNAME + "'s next stream will start %s at %sm EST" % next_stream
    
    # def command_race(self, data):
    #     if on_cooldown(self.cooldowns['!race'], two_mins):
    #         return "%s is trying to register for the Chocobo Racing Lucky Cup, but they forgot to train their chocobo.  Try again in %s seconds." % (self.user, get_cooldown(self.cooldowns['!race'], two_mins))

    #     if self.entry_open == False:
    #         self.entry_open = True
    #         race = ChocoboRace(self)
    #         race.register_racer(self, data)
    #         return "%s has registered for the Chocobo Racing Lucky Cup. Everyone can Join! To join type !race (amount)" % self.user
    #     else:
    #         race.register_racer(self, data)

    def command_merrychristmas(self, data):
        if self.user in self.winners:
            return None
        #print self.prizes
        prize = random.choice(self.prizes)
        self.prizes.pop(self.prizes.index(prize))
        #print self.prizes
        self.winners.append(self.user)
        return 'Congratulations %s!  You have won a %s from the mog station!  Please let %s know which you would like so she can send it!' % (self.user, prize, NICKNAME)
        
        
    # --------------------------------------------- End Local Command Functions ----------------------------------------------

    # --------------------------------------------- Start Remote Command Functions -------------------------------------------

    def command_random(self, data):
        return command_random(self, data)

    # --------------------------------------------- End Remote Command Functions ---------------------------------------------

    # --------------------------------------------- Start Support Functions --------------------------------------------------


    def get_commands_dict(self, user):
        commands = self.commands_public.copy()
        if user in self.regulars + self.moderators + self.admin:
            commands = merge_dicts(commands, self.commands_regulars)
        if user in self.moderators + self.admin:
            commands = merge_dicts(commands, self.commands_moderators)
        if user in self.admin:
            commands = merge_dicts(commands, self.commands_private)
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

    def fmt_currency_name(self, amount):
        if amount == 1:
            return self.currency_name[:-1]
        else:
            return self.currency_name

        
        

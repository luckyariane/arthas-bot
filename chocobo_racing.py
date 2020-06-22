from cooldowns import init_cooldown, on_cooldown, set_cooldown, get_cooldown, two_mins, three_mins
from utils import add_points, sub_points
from random import choice

WIN_MOD = {
    1 : 5,
    2 : 3, 
    3 : 2, 
    4 : 1,
    5 : 1,
    6 : 0.5,
    7 : 0.5,
    8 : 0,
}

WORD_MOD = {
    1 : 'st',
    2 : 'nd', 
    3 : 'rd', 
    4 : 'th',
    5 : 'th',
    6 : 'th',
    7 : 'th',
    8 : 'th',
}

class ChocoboRace():

    def __init__(self, test=False):
        self.test = test
        self.entry_open = False
        self.race_pending = False
        self.open_time = init_cooldown()
        self.racers = dict()
        self.instance = None
        self.choice_list = ['0'] * 10 + ['1'] * 9 + ['2'] * 8 + ['3'] * 7 + ['4'] * 6 + ['5'] * 5 + ['6'] * 4 + ['7'] * 3 + ['8'] * 2 + ['9'] * 1
        self.test = False

    def check_timer(self):
        if self.entry_open:
            if not on_cooldown(self.open_time, two_mins, test=self.test):
                self.entry_open = False
                return "Registration for the Chocobo Racing Lucky Cup is now closed.  The race is starting."
        else:
            if self.racers:
                if on_cooldown(self.open_time, three_mins, test=self.test):
                    return True
                else:
                    #return self.run_race()
                    return self.run_race_real()
    
    def command_race(self, instance, data):
        if not self.instance: self.instance = instance
        if self.entry_open == False:
            if on_cooldown(instance.cooldowns['!race'], two_mins, test=self.test):
                return "%s is trying to register for the Chocobo Racing Lucky Cup, but they forgot to train their chocobo.  Try again in %s seconds." % (self.instance.user, get_cooldown(instance.cooldowns['!race'], two_mins))
            if not self.race_pending:
                if self.register_racer(data):
                    self.entry_open = True
                    self.race_pending = True
                    self.open_time = set_cooldown()
                    return "%s has registered for the Chocobo Racing Lucky Cup. Everyone can join!  To join type: !race <amount>" % self.instance.user
        else:
            self.register_racer(data)
        return True

    def register_racer(self, data):
        if not data[1]: return False
        if self.instance.user not in self.racers:
            try:
                if sub_points(self.instance, self.instance.user, data[1]):
                    self.racers[self.instance.user] = data[1]
                    return True
            except IndexError:
                pass
        return False

    def run_race(self):
        winners = list()
        all_winners = True
        for racer in self.racers.keys():
            result = choice(['win', 'lose'])
            if result == 'win':
                if add_points(self.instance, racer, int(self.racers[racer]) * 2):
                    winners.append(racer)
            else:
                all_winners = False
        self.racers = dict()
        self.instance.cooldowns['!race'] = set_cooldown()
        self.race_pending = False
        if len(winners) == 0:
            return "The briars were everywhere today.  No one won their race."
        if all_winners:
            return "Everyone won their race!  Congratulations %s!" % ', '.join(winners)
        else:
            return "The race is over.  Congratulations to the winners: %s!" % ', '.join(winners)

    def run_race_real(self):
        racers = self.racers.keys()
        npcs = ['npc_a', 'npc_b', 'npc_c', 'npc_d', 'npc_e', 'npc_f']
        while len(racers) < 8:
            npc = choice(npcs)
            if npc not in racers:
                racers.append(npc)

        racer_dict = dict()
        for racer in racers:
            racer_dict[racer] = 0

        for i in range(0,8):
            for racer in racer_dict:
                racer_dict[racer] = self.update_distance(racer_dict[racer])

        return 'The race is over.  Results are: %s' % self.report_placements(racer_dict)

    def update_distance(self, distance):
        return distance + 100 + int(choice(self.choice_list))

    def report_placements(self, racer_dict):
        placements = sorted(racer_dict.items(), key=lambda x:x[1], reverse=True)
        report = list()
        for i in range(0, len(placements)):
            racer = placements[i][0]
            if 'npc_' in racer: continue
            if not self.test: 
                if add_points(self.instance, racer, int(self.racers[racer]) * WIN_MOD[i+1]):
                    report.append('%s%s %s [%s]' % (i + 1, WORD_MOD[i + 1], placements[i][0], int(self.racers[racer] * WIN_MOD[i+1])))
            else: 
                report.append('%s%s %s [%s]' % (i + 1, WORD_MOD[i + 1], placements[i][0], int(self.racers[racer] * WIN_MOD[i+1])))
        return ', '.join(report)        

if __name__ == '__main__':
    r = ChocoboRace()
    r.test = True
    r.racers = {'ari':100, 'winter':500, 'nick':10, 'clay':100}
    print r.run_race_real()


from random import sample, choice
from cooldowns import init_cooldown, set_cooldown, on_cooldown, two_mins
from utils import sub_points

options = dict()
options['Chocobo Race'] = list()
options['Roulettes *'] = ['Expert', 'Leveling', 'Alliance', 'Trials', '50/60/70']
options['Daily Frontlines'] = list()
options['Extreme Mount Farm *'] = ['Innocence', 'Shinryu', 'Tsukyomi', 'Suzaku', 'Seiryu']
options['Hunts'] = list()
options['Maps'] = list()
options['Side Quests'] = list()
options['Trust Dungeons'] = list()
options['Squadron Dungeons'] = list()
options['SHB MSQ on Alt'] = list()
options['Triple Triad'] = list()
options['Deep Dungeon'] = list()

jobs = dict()
jobs['melee'] = ['MNK','NIN','SAM','DRG']
jobs['tank'] = ['PLD','WAR','DRK','GNB']
jobs['caster'] = ['BLM','SMN','RDM']
jobs['ranged'] = ['BRD','MCH','DNC']
jobs['healer'] = ['SCH','AST']


class Content():

    def __init__(self):
        self.voting_open = False
        self.start_time = init_cooldown()
        self.options = dict()
        self.voted = list()

    def check_timer(self):
        if not self.voting_open:
            return True
        elif not on_cooldown(self.start_time, two_mins):
            return self.end_vote()

    def command_content(self, instance, data):
        if not self.voting_open:
            opts = sample(options.keys(), 4)
            for i in range(1,5):
                index = str(i)
                self.options[index] = dict()
                self.options[index]['option'] = opts[i-1]
                self.options[index]['votes'] = 0
            self.voting_open = True
            self.start_time = set_cooldown()
            text = ["Vote for the content you want to see (!content #):"]
            text += ['%s : %s' % (x, self.options[x]['option']) for x in sorted(self.options.keys())]
            return text
        else:
            data = filter(None, data)
            if len(data) > 1 and data[1] in self.options:
                if len(data) == 3:
                    vote_inc = int(data[2]) / 100
                    try:
                        if sub_points(instance, instance.user, vote_inc * 100):
                            self.options[data[1]]['votes'] += vote_inc
                    except ValueError:
                        pass
                if len(data) > 1 and instance.user not in self.voted:
                    self.options[data[1]]['votes'] += 1 
                    self.voted.append(instance.user)
            return True

    def command_job(self, data):
        data = filter(None, data)
        j_list = list()
        if len(data) > 1:
            if data[1] == 'dps':
                data = [data[0], 'melee', 'caster', 'ranged']
            for role in data[1:]:
                role = role.lower()
                if role in jobs:
                    j_list += jobs[role]
        else:
            for role in jobs:
                j_list += jobs[role]
   
        print j_list
        if len(j_list) == 0:
            return "Invalid option.  Use '!job' or '!job [%s]'" % ', '.join(jobs.keys())
        return choice(j_list)

    def end_vote(self):
        max = 0
        for opt in self.options:
            if self.options[opt]['votes'] > max:
                max = self.options[opt]['votes']

        winners = [self.options[o]['option'] for o in self.options if self.options[o]['votes'] == max]
        self.voting_open = False
        return "Viewer's choice: %s" % choice(winners)

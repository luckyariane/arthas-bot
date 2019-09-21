from cooldowns import init_cooldown, on_cooldown, set_cooldown, get_cooldown, two_mins, three_mins
from utils import add_points, sub_points
from random import choice

class ChocoboRace():

    def __init__(self, test=False):
        self.test = test
        self.entry_open = False
        self.open_time = init_cooldown()
        self.racers = dict()
        self.instance = None

    def race_check(self):
        if self.entry_open:
            if not on_cooldown(self.open_time, two_mins, test=self.test):
                self.entry_open = False
                return "Registration for the Chocobo Racing Lucky Cup is now closed.  The race is starting."
        else:
            if self.racers:
                if on_cooldown(self.open_time, three_mins, test=self.test):
                    return True
                else:
                    return self.run_race()
    
    def command_race(self, instance, data):
        if not self.instance: self.instance = instance
        if self.entry_open == False:
            if on_cooldown(instance.cooldowns['!race'], two_mins, test=self.test):
                return "%s is trying to register for the Chocobo Racing Lucky Cup, but they forgot to train their chocobo.  Try again in %s seconds." % (self.instance.user, get_cooldown(instance.cooldowns['!race'], two_mins))
            else:
                if self.register_racer(data):
                    self.entry_open = True
                    self.open_time = set_cooldown()
                    return "%s has registered for the Chocobo Racing Lucky Cup. Everyone can join!  To join type: !race <amount>" % self.instance.user
        else:
            self.register_racer(data)
        return True

    def register_racer(self, data):
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
        if len(winners) == 0:
            return "The briars were everywhere today.  No one won their race."
        if all_winners:
            return "Everyone won their race!  Congratulations %s!" % ', '.join(winners)
        else:
            return "The race is over.  Congratulations to the winners: %s!" % ', '.join(winners)

if __name__ == '__main__':
    pass    

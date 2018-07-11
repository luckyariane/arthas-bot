
ENTRY_OPEN = False

class ChocoboRace():

    def __init__(self):
        self.racers = dict()
    
    def command_race(self, instance, data):
        if ENTRY_OPEN == False:
            d = datetime.now() - self.cooldowns['!race']
            if d.seconds < 120:
                return "%s is trying to register for the Chocobo Racing Lucky Cup, but they forgot to train their chocobo.  Try again in %s seconds." % (instance.user, 120 - d.seconds)
            else:
                __register_racer(instance, data)

    def register_racer(self, instance, data):
        if instance.user not in self.racers:
            try:
                self.racers[instance.user] = data[1]
            except IndexError:
                return True #TODO: Make a default value if none is set
        else: return True

if __name__ == '__main__':
    pass    

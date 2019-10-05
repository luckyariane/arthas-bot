from cooldowns import init_cooldown, set_cooldown, on_cooldown, fifteen_mins
from random import choice

announcements = [
    'Start up a Chocobo Race minigame with !race <amount> to win clovers!',
    'Try !random to test your RNG luck to win or lose clovers!',
    'Check how many clovers you\'ve accumulated so far with !clovers',
    'View the clovers leaderboard with !top5', 
    'See what chat commands are available with !commands',
]

class Announce():

    def __init__(self):
        self.cooldown = init_cooldown()

    def check_timer(self):
        if not on_cooldown(self.cooldown, fifteen_mins):
            self.cooldown = set_cooldown()
            return choice(announcements)
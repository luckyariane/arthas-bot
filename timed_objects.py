from currency import LoyaltyPoints
from chocobo_racing import ChocoboRace
from vote_content import Content
from announcements import Announce

class TimerObjects():
    def __init__(self):
        self.C          = LoyaltyPoints()
        self.CBR        = ChocoboRace()
        self.CONTENT    = Content()
        self.ANNOUNCE   = Announce()

        self.objs = [
            self.C, 
            self.CBR,
            self.CONTENT,
            self.ANNOUNCE
        ]
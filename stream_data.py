from utils import get_webpage, convert_json
from settings import CHANID, OAUTH
from api_parse import H_BASIC
from cooldowns import on_cooldown, init_cooldown, set_cooldown, five_mins, convert_timestamp

class Stream():
    def __init__(self):
        self.url = 'https://api.twitch.tv/kraken/streams/' + CHANID
        self.updateInterval = five_mins

        self.lastUpdate = init_cooldown()
        self.live = False
        self.stream_start = None
        self.game = None

        self.updateStreamData()

    def updateStreamData(self):
        if on_cooldown(self.lastUpdate, self.updateInterval): return

        stream_data = convert_json(get_webpage(self.url, h=H_BASIC))        
        if stream_data['stream'] == None: 
            self.live = False
            self.stream_start = None 
            self.game = None
        else:
            self.live = True 
            self.stream_start = convert_timestamp(stream_data['stream']['created_at'])
            self.game = stream_data['stream']['game']

        print self.live 
        print self.stream_start
        print self.game
        print self.lastUpdate
        self.lastUpdate = set_cooldown()
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

        #stream_data = convert_json(get_webpage(self.url, h=H_BASIC))
        stream_data = convert_json("""{
   "stream": {
      "_id": 23932774784,
      "game": "BATMAN - The Telltale Series",
      "viewers": 7254,
      "video_height": 720,
      "average_fps": 60,
      "delay": 0,
      "created_at": "2016-12-14T22:49:56Z",
      "is_playlist": false,
      "preview": {
         "small": "https://static-cdn.jtvnw.net/previews-ttv/live_user_dansgaming-80x45.jpg",
         "medium": "https://static-cdn.jtvnw.net/previews-ttv/live_user_dansgaming-320x180.jpg",
         "large": "https://static-cdn.jtvnw.net/previews-ttv/live_user_dansgaming-640x360.jpg",
         "template": "https://static-cdn.jtvnw.net/previews-ttv/live_user_dansgaming-{width}x{height}.jpg"
      },
      "channel": {
         "mature": false,
         "status": "Dan is Batman? - Telltale's Batman",
         "broadcaster_language": "en",
         "display_name": "DansGaming",
         "game": "BATMAN - The Telltale Series",
         "language": "en",
         "_id": 7236692,
         "name": "dansgaming",
         "created_at": "2009-07-15T03:02:41Z",
         "updated_at": "2016-12-15T01:33:58Z",
         "partner": true,
         "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/dansgaming-profile_image-76e4a4ab9388bc9c-300x300.png",
         "video_banner": "https://static-cdn.jtvnw.net/jtv_user_pictures/dansgaming-channel_offline_image-d3551503c24c08ad-1920x1080.png",
         "profile_banner": "https://static-cdn.jtvnw.net/jtv_user_pictures/dansgaming-profile_banner-4c2b8ece8cd010b4-480.jpeg",
         "profile_banner_background_color": null,
         "url": "https://www.twitch.tv/dansgaming",
         "views": 63906830,
         "followers": 538598
      }
   }
}""")
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
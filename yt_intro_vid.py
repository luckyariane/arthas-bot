import urllib2, re, random, json
from cooldowns import init_cooldown, on_cooldown, set_cooldown, thirty_mins
from settings import MY_YT_API_KEY, YT_CHANNEL_ID

YT_URL = 'http://www.youtube.com/watch?v=%s&start=%s'

class YTVideo():
    def __init__(self):
        self.cooldown = init_cooldown()
        self.main()

    def getAPIData(self, api_str):
        url = 'https://www.googleapis.com/youtube/v3/' + api_str
        request = urllib2.Request(url)
        return json.loads(urllib2.urlopen(request).read())

    def makeTimestamp(self, h, m, s):
        # convert to seconds
        ts = s
        ts += m * 60
        ts += h * 60 * 60
        return ts

    def getRandomTime(self, time):
        h = 0
        m = 0
        s = 0

        t = re.search('PT(?P<hour>[0-9]+H)?(?P<min>[0-9]+M)?(?P<sec>[0-9]+S)?', time)

        if t:
            if t.group('hour'):
                h = int(t.group('hour').upper().replace('H', ''))
            if t.group('min'):
                m = int(t.group('min').upper().replace('M', ''))
            if t.group('sec'):
                s = int(t.group('sec').upper().replace('S', ''))

        ts = self.makeTimestamp(h, m, s)    
        # check length isn't less than 30 mins
        if ts < 30 * 60:
            print 'ERROR: Video Length Too Short'
            return 0

        ts = random.randint(10 * 60, ts - 20 * 60)
        return ts

    def getYTVideoWithTimestamp(self, video_dict, item_val=0):
        # TEMP BYPASS
        # video_id = '6NfgIs0qkdY'
        # video_len_dict = self.getAPIData('videos?id=%s&part=contentDetails&key=%s' % (video_id, MY_YT_API_KEY))
        # video_length = video_len_dict['items'][0]['contentDetails']['duration']
        # return (video_id, self.getRandomTime(video_length), video_dict)
        # END TEMP BYPASS

        # get video id
        if not video_dict:
            video_dict = self.getAPIData('search?key=%s&channelId=%s&part=snippet,id&order=date&maxResults=10&type=video' % (MY_YT_API_KEY, YT_CHANNEL_ID))
        #print video_dict['items'][item_val]
        video_id = video_dict['items'][item_val]['id']['videoId']

        # get video length
        video_len_dict = self.getAPIData('videos?id=%s&part=contentDetails&key=%s' % (video_id, MY_YT_API_KEY))
        video_length = video_len_dict['items'][0]['contentDetails']['duration']

        return (video_id, self.getRandomTime(video_length), video_dict)

    def makeWebPage(self, video_id, timestamp):
        html = """<html>
        <iframe width="1422" height="800" src="https://www.youtube.com/embed/%s?controls=0&amp;start=%s&autoplay=1" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </html>""" % (video_id, timestamp)

        with open('D:\Stream\Web Overlay\yt_random_video.html', 'w') as f:
            f.write(html)
            f.close()
        # vid_url = YT_URL % (video_id, timestamp)
        print 'Updated Youtube Video to [ %s ]' % YT_URL % (video_id, timestamp)

    def main(self):
        if on_cooldown(self.cooldown, thirty_mins):
            return

        video_dict = None

        # loop until we get a long enough video
        for count in range(0, 10):
            video_id, timestamp, video_dict = self.getYTVideoWithTimestamp(video_dict, count)
            if timestamp != 0: break

        self.makeWebPage(video_id, timestamp)
        self.cooldown = set_cooldown()


if __name__ == '__main__':
    yt = YTVideo()
    yt.main()
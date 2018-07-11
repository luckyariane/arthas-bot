from datetime import datetime, timedelta
import urllib2
import json
import random
import settings 

SESSION_LATEST_DONATOR = settings.ROOT_PATH + r'\Data\Twitch Alerts\session_most_recent_donator.txt'
SESSION_DONATORS = settings.ROOT_PATH + r'\Data\Twitch Alerts\session_donators.txt'
LATEST_SUB = settings.ROOT_PATH + r'\Data\Twitch Alerts\most_recent_subscriber.txt'
CLIENT_ID = settings.CLIENT_ID


class streamDataDisplay():
    def __init__(self):
        self.now = datetime.now()
        self.cooldown = self.now - timedelta(seconds=400)
        self.options = [self.latest_follower] * 10 + [self.recent_follower] * 5 #* 10 + [self.session_latest_donator] * 3 + [self.session_recent_donator]
        self.html_file_live = settings.ROOT_PATH + r'\Web Overlay\myStreamPanelAnimations.html'
        self.html_file_base = settings.ROOT_PATH + r'\Web Overlay\myStreamPanelSource.html'
        self.label_file = settings.ROOT_PATH + r'\Data\random_label.txt'
        self.data_file = settings.ROOT_PATH + r'\Data\random_data.txt'
        self.channel_name = settings.CHAN.replace('#', '')
        
    def __api_call(self, api):
        url = 'https://api.twitch.tv/kraken/' + api
        request = urllib2.Request(url, headers={"Client-ID" : CLIENT_ID})
        return self.__convert_json(urllib2.urlopen(request).read())

    def __convert_json(self, data):
        return json.loads(data)

    def __pad_name(self, name):
        if '$' and '.00' in name:
            name = name.split('.')[0]
        name = name.replace('CA$', '$')
        l = len(name)
        if l > 21:
            return name[:21]
        d = (21 - l) / 2
        return ' ' * d + name

    def update(self):
        self.now = datetime.now()
        d = self.now - self.cooldown
        if d.seconds < 300:
            return

        while True:
            label, data = random.choice(self.options)()
            if len(data) > 1:
                break

        image = '<image id="cloverEmote" src="%s\Emotes\heart.png">' % settings.ROOT_PATH
        if 'subscribe' in label.lower():
            image = '<image id="cloverEmote" src="%s\Emotes\clover_lg.png">' % settings.ROOT_PATH
            
        with open(self.html_file_base, 'r') as b:
            html = b.read()
            with open(self.html_file_live, 'w') as l:
                l.write(html % (label.upper(), data, image))
                l.close()
            b.close()

        with open(self.label_file, 'w') as f:
            f.write(label)
        with open(self.data_file, 'w') as f:
            f.write(data)

        self.cooldown = self.now
        print '#' + data + '#'

    def session_latest_donator(self):
        with open(SESSION_LATEST_DONATOR, 'r') as f:
            data = f.read().strip()
        return ('Latest Tip', self.__pad_name(data))

    def session_recent_donator(self):
        with open(SESSION_DONATORS, 'r') as f:
            data = f.read().split(',')
        if len(data) > 2:
            return ('Recent Tip', self.__pad_name(random.choice(data[1:-1]).strip()))

    def recent_follower(self):
        follow_dict = self.__api_call('channels/' + self.channel_name + '/follows')
        user_list = list()
        for user in follow_dict['follows'][1:6]:
            user_list.append(user['user']['display_name'])
        for user in follow_dict['follows'][6:]:
            d = self.now - datetime.strptime(user['created_at'].split('T')[0], '%Y-%m-%d')
            if d.days <= 7:
                user_list.append(user['user']['display_name'])
        return ('Recent Follower', self.__pad_name(random.choice(user_list)))        

    def latest_follower(self):
        follow_dict = self.__api_call('channels/' + self.channel_name + '/follows')
        latest_follower = follow_dict['follows'][0]['user']['display_name']
        return ('Latest Follower', self.__pad_name(latest_follower))

    def latest_sub(self):
        with open(LATEST_SUB, 'r') as f:
            data = f.read().strip()
        return ('Latest Subscriber', self.__pad_name(data))
    
    def test(self):
        follow_dict = self.__api_call('channels/' + self.channel_name + '/follows')
        user_list = list()
        for user in follow_dict['follows'][1:]:
            user_list.append(user['user']['display_name'])
        for user in user_list:
            print self.__pad_name(user)

if __name__ == '__main__':
    api = streamDataDisplay()
    api.update()
    api.test()


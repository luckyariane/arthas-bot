from datetime import datetime, timedelta
import json
import random
from settings import ROOT_PATH, CLIENT_ID, CHANID, OAUTH, CHAN, HELIX_OAUTH
from utils import get_webpage, convert_json

SESSION_LATEST_DONATOR = ROOT_PATH + r'\Data\Twitch Alerts\session_most_recent_donator.txt'
SESSION_DONATORS = ROOT_PATH + r'\Data\Twitch Alerts\session_donators.txt'
LATEST_SUB = ROOT_PATH + r'\Data\Twitch Alerts\most_recent_subscriber.txt'
CLIENT_ID = CLIENT_ID

# api headers
H_BASIC = {
    'Accept' : 'application/vnd.twitchtv.v5+json', # this can be deleted after Sept 12, 2019
    'Client-ID' : CLIENT_ID,
}

# Kraken v5
H_AUTH_OLD = {
    'Accept' : 'application/vnd.twitchtv.v5+json', # this can be deleted after Sept 12, 2019
    'Client-ID' : CLIENT_ID,
    'Authorization' : 'OAuth %s' % OAUTH,    
}

# Helix
H_AUTH = {    
    'Client-ID' : CLIENT_ID,
    'Authorization' : 'Bearer %s' % HELIX_OAUTH,
}

class streamDataDisplay():
    def __init__(self):
        self.now = datetime.now()
        self.cooldown = self.now - timedelta(seconds=400)
        self.options = [self.latest_follower] * 10 + [self.recent_follower] * 5
        if CHANID and OAUTH:
            print 'Using Kraken v5 for sub data'
            self.options += [self.latest_sub] * 5 + [self.recent_sub] * 10 
        # elif CHANID and HELIX_OAUTH:
        #     print 'Using Helix for sub data'
        #     self.options += [self.latest_sub_helix] * 5 + [self.recent_sub_helix] * 10
        self.html_file_live = ROOT_PATH + r'\Web Overlay\myStreamPanelAnimations.html'
        self.html_file_base = ROOT_PATH + r'\Web Overlay\myStreamPanelSource.html'
        self.label_file = ROOT_PATH + r'\Data\random_label.txt'
        self.data_file = ROOT_PATH + r'\Data\random_data.txt'
        self.channel_name = CHAN.replace('#', '')
        
    def __api_call_old(self, api, auth=False):
        url = 'https://api.twitch.tv/kraken/' + api
        if auth:
            page = get_webpage(url, h=H_AUTH_OLD)
        else:
            page = get_webpage(url, h=H_BASIC)
        return convert_json(page)

    def __api_call(self, api, auth=False):
        url = 'https://api.twitch.tv/helix/' + api
        if auth:
            page = get_webpage(url, h=H_AUTH)
        else:
            page = get_webpage(url, h=H_BASIC)
        return convert_json(page)

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

        image = r'<image id="cloverEmote" src="%s\Emotes\heart.png">' % ROOT_PATH
        if 'subscribe' in label.lower():
            image = r'<image id="cloverEmote" src="%s\Emotes\clover_lg.png">' % ROOT_PATH
            
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
        follow_dict = self.__api_call('users/follows?to_id=' + CHANID)
        user_list = list()
        for user in follow_dict['data'][1:6]:
            user_list.append(user['from_name'])
        for user in follow_dict['data'][6:]:
            d = self.now - datetime.strptime(user['followed_at'].split('T')[0], '%Y-%m-%d')
            if d.days <= 7:
                user_list.append(user['from_name'])
        return ('Recent Follower', self.__pad_name(random.choice(user_list)))        

    def latest_follower(self):
        follow_dict = self.__api_call('users/follows?to_id=' + CHANID)
        latest_follower = follow_dict['data'][0]['from_name']
        return ('Latest Follower', self.__pad_name(latest_follower))

    def __get_sub_data(self, q_type=None): # q_type options: latest
        sub_dict = self.__api_call_old('channels/%s/subscriptions?direction=desc' % CHANID, auth=True)
        sub_data = dict()
        for sub in sub_dict['subscriptions']:
            if sub['user']['name'] == self.channel_name: continue
            sub_data[sub['user']['updated_at']] = (sub['user']['display_name'], sub['created_at'])

        recent_subs = list()
        latest = None
        # TODO: Add check for no recent subs, to not break the display
        for user in sorted(sub_data.keys(), reverse=True):
            if latest:
                d = self.now - datetime.strptime(user.split('T')[0], '%Y-%m-%d')
                if d.days <= 31:
                    recent_subs.append(sub_data[user][0])
            else:
                latest = sub_data[user][0]
                if q_type == 'latest':
                    return latest
        return recent_subs        

    def __get_sub_data_helix(self, q_type=None): # q_type options: latest
        # Don't use this until there's a way to sort by date
        sub_list = list()
        sub_dict = self.__api_call('subscriptions?broadcaster_id=%s' % CHANID, auth=True)
        print sub_dict
        while True:
            sub_list += sub_dict['data']
            page = sub_dict['pagination']['cursor']
            sub_dict = self.__api_call('subscriptions?broadcaster_id=%s&after=%s' % (CHANID, page), auth=True)
            print sub_dict
            if len(sub_dict['data']) == 0: break
        return 'Test'
        # sub_data = dict()
        # for sub in sub_dict['subscriptions']:
        #     if sub['user']['name'] == self.channel_name: continue
        #     sub_data[sub['user']['updated_at']] = (sub['user']['display_name'], sub['created_at'])

        # recent_subs = list()
        # latest = None
        # # TODO: Add check for no recent subs, to not break the display
        # for user in sorted(sub_data.keys(), reverse=True):
        #     if latest:
        #         d = self.now - datetime.strptime(user.split('T')[0], '%Y-%m-%d')
        #         if d.days <= 31:
        #             recent_subs.append(sub_data[user][0])
        #     else:
        #         latest = sub_data[user][0]
        #         if q_type == 'latest':
        #             return latest
        # return recent_subs

    def recent_sub(self):
        user_list = self.__get_sub_data()
        return ('Recent Subscriber', self.__pad_name(random.choice(user_list))) 

    def recent_sub_helix(self):
        user_list = self.__get_sub_data_helix()
        return ('Recent Subscriber', self.__pad_name(random.choice(user_list)))  

    def latest_sub(self):
        latest_sub = self.__get_sub_data(q_type='latest')
        return ('Latest Subscriber', self.__pad_name(latest_sub))

    def latest_sub_helix(self):
        latest_sub = self.__get_sub_data_helix(q_type='latest')
        return ('Latest Subscriber', self.__pad_name(latest_sub))
    
    def test(self):
        follow_dict = self.__api_call('users/follows?to_id=' + CHANID)
        latest_follower = follow_dict['data'][0]['from_name']
        return ('Latest Follower', self.__pad_name(latest_follower))

    def getYourChannelID(self, followed_channel):
        follow_dict = self.__api_call('channels/' + followed_channel + '/follows')
        for user in follow_dict['follows']:
            if user['user']['name'] == self.channel_name:
                print 'Channel id for user[%s] is: %s' % (self.channel_name, user['user']['_id'])

if __name__ == '__main__':
    api = streamDataDisplay()
    api.update()
    #print api.latest_sub_helix()
    print api.latest_sub()
    #api.test()

    # uncomment the lines below and run this file to get your channel id
    #api = streamDataDisplay()
    #api.getYourChannelID('<update me>') # enter the name of a channel you've recently followed




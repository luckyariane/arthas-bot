import json
from datetime import datetime, timedelta
import pickle 
import urllib2
import re


def TokenRefreshTime(path):
    print 'Checking if OAUTH token needs refreshing...'
    with open(path + r'\Data\TwitchAPI\refresh_access_time.pkl', 'a+') as f:
        f.seek(0)
        if len(f.read().strip()) == 0:
            # date = datetime.now()
            # pickle.dump(date, f)
            # f.close()
            print 'Could not find last refresh time...'
            return True
        else:
            f.seek(0)
            refresh_time = datetime.today() - timedelta(days=15)
            date = pickle.load(f)
            if date < refresh_time:
                print 'Time to refresh token'
                return True
            else:
                print 'Token is still valid'
                return False

def RefreshToken(path, refresh_token):
    print 'Refreshing token...'
    url = 'https://twitchtokengenerator.com/api/refresh/' + refresh_token
    request = urllib2.Request(url)
    data = json.loads(urllib2.urlopen(request).read())
    if 'token' in data:
        new_token = data['token']
        with open(path + r'\arthas-bot\local_settings.py', 'r+') as f:
            settings = f.read()
            settings = re.sub("OAUTH = '.*' # generated from https://twitchtokengenerator.com", "OAUTH = '%s' # generated from https://twitchtokengenerator.com" % new_token, settings)
            f.seek(0)
            f.write(settings)
            f.close()
        with open(path + r'\Data\TwitchAPI\refresh_access_time.pkl', 'w+') as f:
            pickle.dump(datetime.now(), f)
            f.close()
        print 'Token has been refreshed!'
    else:
        print data


if __name__ == '__main__':
    from local_settings import ROOT_PATH, REFRESH_TOKEN
    if TokenRefreshTime(ROOT_PATH): 
        RefreshToken(ROOT_PATH, REFRESH_TOKEN)

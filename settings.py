try:
    from local_settings import CHAN, NICK, PASS, ROOT_PATH, CLIENT_ID, REGULARS, MODERATORS, CHANNEL_NAME, NICKNAME, CHANID, OAUTH, HELIX_OAUTH, MY_YT_API_KEY, YT_CHANNEL_ID
    print 'local_settings FOUND'
    
except:
    # user specific settings

    #################################
    # BEGIN EDITABLE DATA           #
    # update <> fields to your      #
    # personal info                 #
    # ----------------------------- #
    # Note: Data configured here    #
    # will only be read if file     #
    # local_settings.py does not    #
    # exist.  Delete                #
    # local_settings.py to          #
    # regenerate from data          #
    # configured below.             #
    #################################
    user_settings = """

# connect to twitch channel settings
CHAN = '#<channel>' # twitch channel to connect to
NICK = '<username>' # twitch username to connect as
PASS = 'oauth:<key>'  # www.twitchapps.com/tmi/ will help to retrieve the required authkey

# path to save files to.  This should be separate from where the bot files are located
ROOT_PATH = r'<path>'

# add user names in quotes and comma separated eg ['user1', 'user2']
REGULARS = []
MODERATORS = []

# update this if there's a name the streamer goes by different than the channel name
NICKNAME = ''

# required for getting subscriber data
CHANID = None # your numerical channel id
OAUTH = None
HELIX_OAUTH = None

# Instructions for getting OAUTH:
# use https://twitchapps.com/tokengen to get your OAUTH value.  Use 
# CLIENT_ID 074ub1uhqkvefhdgco9m53wq76pngk (or register your own app with Twitch)
# and request the 'channel_subscriptions' scope.  

# Instructions for getting CHANID:
# The easy no auth way to do this is to follow someone else's channel, and then open
# api_parse.py and follow the instructions at the bottom of the file

# Youtube API Settings
MY_YT_API_KEY = None
YT_CHANNEL_ID = None

# TODO instructions for getting Youtube data

"""
    #################################
    # END EDITABLE DATA             #
    #################################

    user_settings += """

CHANNEL_NAME = CHAN.replace('#', '')
if not NICKNAME:
    NICKNAME = CHANNEL_NAME

"""

    default_settings = """

# connect to API setting
CLIENT_ID = '8zlinrdiim7fmnr7tejupimkhkfm2t'
#CLIENT_SECRET = '<secret key>'
"""






    # write configured data to new file
    with open('local_settings.py', 'w+') as f:
        f.write(user_settings)
        f.write(default_settings)
        f.close()

    from local_settings import CHAN, NICK, PASS, ROOT_PATH, CLIENT_ID, REGULARS, MODERATORS, CHANNEL_NAME, NICKNAME, CHANID, OAUTH, HELIX_OAUTH, MY_YT_API_KEY, YT_CHANNEL_ID
    print 'local_setting CREATED'



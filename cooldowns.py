from datetime import datetime, timedelta

one_min = 60
two_mins = 120
three_mins = 180
five_mins = 300
fifteen_mins = 15 * 60
thirty_mins = 30 * 60

def on_cooldown(timestamp, interval, test=False):
    if test:
        interval = interval / 10
    d = datetime.now() - timestamp
    if d.seconds < interval: return True
    return False

def get_cooldown(timestamp, interval):
    d = datetime.now() - timestamp
    return interval - d.seconds

def set_cooldown():
    return datetime.now()

def init_cooldown():
    return datetime.now() - timedelta(seconds=50000)


# other datetime functions
def convert_timestamp(timestamp, fmt='%Y-%m-%dT%H:%M:%SZ'):
    return datetime.strptime(timestamp, fmt)

def get_timestamp():
    return datetime.now()
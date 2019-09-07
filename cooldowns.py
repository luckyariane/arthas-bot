from datetime import datetime, timedelta

five_mins = 300
one_min = 60

def on_cooldown(timestamp, interval):
    d = datetime.now() - timestamp
    if d.seconds < interval: return True
    return False

def reset_cooldown():
    return datetime.now()

def set_cooldown():
    return datetime.now() - timedelta(seconds=50000)
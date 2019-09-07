import random
from datetime import datetime
import settings

verbs = ['gains'] * 10 + ['loses'] * 10 + ['gives']

# dj_count = 0
# dj_joke = False

timeout = dict()

def command_random(instance, data):
    global timeout
    if instance.user in timeout:
        d = datetime.now() - timeout[instance.user]
        if d.seconds < 60:
            return True    
    timeout[instance.user] = datetime.now()
    # ##temp joke
    # global dj_joke
    # if dj_joke == False:
        # global dj_count
        # if dj_count > 10:
            # if 'dj_rezurrection' in instance.recent_chatters:
                # instance.cur.execute('SELECT amount FROM currency WHERE user = "dj_rezurrection"')
                # current_points = instance.cur.fetchone()[0]
                # dj_joke = True
                # return 'dj_rezurrection loses %s gil (100%%)' % current_points
        # dj_count += 1
    # ##end temp joke
    users = list(instance.recent_chatters)
    users.append(settings.CHANNEL_NAME)
    users += [instance.user] * 95
    user = random.choice(users)

    other_users = list(instance.recent_chatters)
    if settings.CHANNEL_NAME not in other_users:
        other_users.append(settings.CHANNEL_NAME)
    if user in other_users:
        other_users.pop(other_users.index(user))
    if len(other_users) == 0:
        other_user = None
    else:
        other_user = random.choice(other_users)

    verb = random.choice(verbs)
    if other_user == None and verb == 'gives':
        verb = 'gains'

    percent = random.choice(range(1, 11))

    instance.cur.execute('SELECT amount FROM currency WHERE user = ?', (user,))
    try:
        current_points = int(instance.cur.fetchone()[0])
    except TypeError:
        return "Sorry %s you're not in the database yet.  Try again in 5 mins" % user 
    
    change_points = int(round(current_points * (float(percent)/float(100)), 0))

    if verb in ['gains', 'loses']:
        if verb == 'gains':
            instance.cur.execute('UPDATE currency SET amount = amount + ? WHERE user = ?', (change_points, user))
        elif verb == 'loses':
            instance.cur.execute('UPDATE currency SET amount = amount - ? WHERE user = ?', (change_points, user))
        instance.con.commit()
        return '%s %s %s gil (%s%%)' % (user, verb, change_points, percent)
    elif verb == 'gives':
        instance.cur.execute('UPDATE currency SET amount = amount - ? WHERE user = ?', (change_points, user))
        instance.cur.execute('UPDATE currency SET amount = amount + ? WHERE user = ?', (change_points, other_user))
        instance.con.commit()
        return '%s %s %s gil (%s%%) to %s' % (user, verb, change_points, percent, other_user)

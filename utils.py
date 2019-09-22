import urllib2, json
from settings import CLIENT_ID, OAUTH, HELIX_OAUTH
from cooldowns import get_timestamp

def get_top_users(instance, num):
    r = instance.cur.execute('SELECT user, amount FROM currency WHERE user != "arthasbot" ORDER BY amount DESC LIMIT ?', (num,))
    return r.fetchall()

def add_points(instance, user, change_points):
    validate_user(instance, [user])
    r = instance.cur.execute('UPDATE currency SET amount = amount + ? WHERE user = ?', (change_points, user))
    return success(instance, r.rowcount) 
    
def add_points_multi(instance, user_list, change_points, time_tracking=False):
    validate_user(instance, user_list)
    r = instance.cur.execute('UPDATE currency SET amount = amount + ? WHERE user in ({seq})'.format(seq=','.join(['?'] * len(user_list))), tuple([change_points] + user_list))
    if success(instance, r.rowcount) and time_tracking:
        r = instance.cur.execute('UPDATE currency SET time_increments = time_increments + 1 WHERE user in ({seq})'.format(seq=','.join(['?'] * len(user_list))), tuple(user_list))
    return success(instance, r.rowcount) 

def sub_points(instance, user, change_points):
    validate_user(instance, [user])
    if get_points(instance, user) < int(change_points): return False
    r = instance.cur.execute('UPDATE currency SET amount = amount - ? WHERE user = ?', (change_points, user))
    return success(instance, r.rowcount)

def get_points(instance, user):
    validate_user(instance, [user])
    instance.cur.execute('SELECT amount FROM currency WHERE user = ?', (user,))
    return int(instance.cur.fetchone()[0])

def validate_user(instance, users):
    if len(users) == 1:     user_tuple = (users[0],)
    else:                   user_tuple = tuple(users)

    instance.cur.execute('SELECT user FROM currency WHERE user in ({seq})'.format(seq=','.join(['?'] * len(users))), user_tuple)
    db_user_list = [str(x) for x, in instance.cur.fetchall()]

    new_users = 0
    for user in users:
        if user not in db_user_list:
            new_users += 1
            sql = 'INSERT INTO currency(user, timestamp, amount, time_increments) VALUES(?, ?, ?, ?)'
            instance.cur.execute(sql, (user, get_timestamp(), 0, 0))
    success(instance, new_users)    

def success(instance, value):
    if value == 0: 
        return False
    else: 
        instance.con.commit()
        return True

def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def update_file(file_name, data):
    with open(file_name, 'w') as f:
        f.write(str(data))

def read_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()

def append_file(file_name, data):
    with open(file_name, 'a') as f:
        f.write(str(data))

def get_webpage(url, h=None):
    if h:
        request = urllib2.Request(url, headers=h)
    else: 
        request = url
    return urllib2.urlopen(request).read()
  
def convert_json(data):
    return json.loads(data)


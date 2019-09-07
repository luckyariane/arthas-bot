import urllib2, json
from settings import CLIENT_ID, OAUTH, HELIX_OAUTH

def add_points(instance, user, change_points):
    r = instance.cur.execute('UPDATE currency SET amount = amount + ? WHERE user = ?', (change_points, user))
    return success(r.rowcount) 
    
def add_points_multi(instance, user_list, change_points, time_tracking=False):
    r = instance.cur.execute('UPDATE currency SET amount = amount + ? WHERE user in ({seq})'.format(seq=','.join(['?'] * len(user_list))), tuple([change_points] + user_list))
    if success(r.rowcount) and time_tracking:
        r = instance.cur.execute('UPDATE currency SET time_increments = time_increments + 1 WHERE user in ({seq})'.format(seq=','.join(['?'] * len(user_list))), tuple(user_list))
    return success(r.rowcount) 

def sub_points(instance, user, change_points):
    r = instance.cur.execute('UPDATE currency SET amount = amount - ? WHERE user = ?', (change_points, user))
    return success(r.rowcount)

def get_points(instance, user):
    instance.cur.execute('SELECT amount FROM currency WHERE user = ?', (user,))
    return int(instance.cur.fetchone()[0])

def success(value):
    if value == 0: return False
    else: return True

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


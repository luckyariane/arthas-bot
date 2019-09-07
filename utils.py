import datetime

def add_points(instance, user, change_points):
    r = instance.cur.execute('UPDATE CurrencyUser SET Points = Points + %s WHERE Name in ("%s")' % (change_points, user))
    return success(r.rowcount) 

def sub_points(instance, user, change_points):
    r = instance.cur.execute('UPDATE CurrencyUser SET Points = Points - %s WHERE Name in ("%s")' % (change_points, user))
    return success(r.rowcount)

def get_points(instance, user):
    instance.cur.execute('SELECT Points FROM CurrencyUser WHERE Name = "%s"' % user)
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

#def cooldown(timer, time, user=None):
#    d = datetime.now() - timer
#    if d.seconds < time:
        

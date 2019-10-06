import re
import socket
import commands
import api_parse
import yt_intro_vid
import settings
import refresh_api
from stream_data import Stream
from timed_objects import TimerObjects

# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.chat.twitch.tv"                     # Hostname of the IRC-Server in this case twitch's
PORT = 6667                                     # Default IRC-Port
CHAN = settings.CHAN                            # Channelname = #{Nickname}
NICK = settings.NICK                            # Nickname = Twitch username
PASS = settings.PASS                            # www.twitchapps.com/tmi/ will help to retrieve the required authkey

STREAM = Stream()
DISPLAY = api_parse.streamDataDisplay()
YT = yt_intro_vid.YTVideo()
TIMEOBJS = TimerObjects()
COMS = commands.Commands(TIMEOBJS)
# --------------------------------------------- End Settings -------------------------------------------------------



# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(con, msg):
    con.send(bytearray('PONG %s\r\n' % msg, 'UTF-8'))

def send_message(con, chan, msg, user='bot'):
    con.send(bytearray('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))

def send_nick(con, nick, user='bot'):
    con.send(bytearray('NICK %s\r\n' % nick, 'UTF-8'))
        
def send_pass(con, password, user='bot'):
    con.send(bytearray('PASS %s\r\n' % password, 'UTF-8'))

def join_channel(con, chan):
    con.send(bytearray('JOIN %s\r\n' % chan, 'UTF-8'))

def part_channel(con, chan):
    con.send(bytearray('PART %s\r\n' % chan, 'UTF-8'))
# --------------------------------------------- End Functions ------------------------------------------------------


# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result


def parse_message(con, user, msg, options):
    if len(msg) >= 1:
        msg = msg.split(' ')
        if msg[0] in options:
            rsp = options[msg[0]](msg)
            if rsp == False:
                send_message(con, CHAN, 'Error Parsing Command')
                print('__ArthasBot' + ": " + 'Error Parsing Command')
            elif rsp == True:
                pass
            elif type(rsp) == list:
                for item in rsp:
                    send_message(con, CHAN, item)
                    print('__ArthasBot' + ": " + item)
            else:
                send_message(con, CHAN, rsp)
                print('__ArthasBot' + ": " + rsp)
        elif msg[0] == '!commands':
            c = 'Available Commands: ' + ', '.join(sorted(options.keys()))
            send_message(con, CHAN, c)
            print('__ArthasBot' + ": " + c)

def disconnect(con):
    part_channel(con, CHAN)
    con.close()

def main():
    con = socket.socket()
    con.connect((HOST, PORT))

    con.settimeout(10.0)

    send_pass(con, PASS)
    send_nick(con, NICK)
    join_channel(con, CHAN)

    data = ''

    while True:
        try:
            STREAM.updateStreamData()
            if STREAM.live: 
                DISPLAY.update()
                YT.main()
                for obj in TIMEOBJS.objs:
                    msg_data = obj.check_timer()
                    if type(msg_data) == str:
                        send_message(con, CHAN, msg_data)

            data = data+con.recv(1024).decode('UTF-8')
            data_split = re.split(r"[~\r\n]+", data)
            data = data_split.pop()

            for line in data_split:
                try:
                    line = str.rstrip(str(line))
                    line = str.split(str(line))
                except UnicodeEncodeError: continue            

                if len(line) >= 1:
                    if line[0] == 'PING':
                        send_pong(con, line[1])
                        
                    try:
                        if line[1] == 'PRIVMSG':
                            sender = get_sender(line[0])
                            if sender not in COMS.recent_chatters and sender.lower() != 'arthasbot':
                                if len(COMS.recent_chatters) > 4:
                                    COMS.recent_chatters.pop(0)
                                COMS.recent_chatters.append(sender)
                            COMS.set_user(sender)
                            options = COMS.get_commands_dict(sender)                    
                            message = get_message(line)
                            print(sender + ": " + message)
                            parse_message(con, sender, message, options)
                    except IndexError:
                        print 'INDEX ERROR: %s' % line
        except socket.timeout:
            #print '\tTIMED OUT - NON FATAL?'
            continue
##        except Exception, e:
##            print e
##            disconnect(con)
##            break


if __name__ == '__main__':
    if refresh_api.TokenRefreshTime(settings.ROOT_PATH): 
        refresh_api.RefreshToken(settings.ROOT_PATH, settings.REFRESH_TOKEN)
    while True:
        print '        >>>>Restarting Bot!'
        main()

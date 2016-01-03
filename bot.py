import discord
import urllib.request
import urllib.parse
import re
from datetime import datetime,tzinfo,timedelta
import threading
from random import randint

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

class FakeMember():
    def __init__(self, name):
        self.name = name

string1 = "[ "
string2 = '"},'
EST = Zone(-5,False,'EST')
JST = Zone(9,False,'JST')
oldstr = ''
finalstr = ''
date = ''
decisionbotid = '130739227351711744'
#decisionbotid = '131523343139602432'# --- Kodi's testbot
enfoniusid = '125045788958130177'
EQDict = {}
IDDict = {}
EQTest = {}
EQPostDict = {}

parsestarted = True

#password in infos.txt
fp_infos = open("infos.txt", "r")

user = fp_infos.readline()
user = user.replace('\n', '')

password = fp_infos.readline()
password = password.replace('\n', '')

fp_infos.close()
client = discord.Client()
client.login(user, password)


#debug method
def generateList(message, inputstring):
    pCount = 1
    playerlist = ''
    for member in EQTest[message.channel.name]:
            playerlist += (str(pCount) + ". " + member.name + '\n')
            pCount+=1
        
    while pCount < 13:
        playerlist += (str(pCount) + ".\n")
        pCount+=1
        
    global oldmessage
    try:
        client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring)
    except:
        print('posting first list')
        EQPostDict[message.channel.name] = client.send_message(message.channel, playerlist + inputstring)
    

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def findEQ():
    global oldstr
    global finalstr
    global date
    global announcementChannel
    
    threading.Timer(300, findEQ).start()
    url = 'http://pso2emq.flyergo.eu/api/v2'
    values = {'s':'basics','sumbit':'search'}
    ship1substr = 'Ship01:'
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')
    req =  urllib.request.Request(url,data)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    date = ('*' + str(datetime.now(JST).strftime('%H:%M %Z')) + '      ' + str(datetime.now(EST).strftime('%H:%M %Z')) + '*')
    string3 = find_between(str(respData), string1, string2)
    stringx = find_between(str(respData), string1, ']')
            
    if ship1substr in string3:
        #UGLY PARSE BEING
        stringxx = '[ ' + stringx + ']'
        string4 = find_between(string3, 'Ship02', 'Ship03')
        string5 = string4.replace("\\n", " ")
        string6 = string5.replace('\\', "\n")
        finalstr = stringxx + '\nShip02' + string6
        #UGLY PARSE END
        if '\nShip02: -' in finalstr:
            if oldstr != finalstr:
                noeqstr = stringxx + '\nThere is no EQ going on in Ship02 at the given hour.'
                client.send_message(announcementChannel, str(date) + '\n' + str(noeqstr))
                print(date)
                print(noeqstr)
                oldstr = finalstr
        elif oldstr != finalstr:
            client.send_message(announcementChannel, '@everyone\n' + str(date) + '\n' + str(finalstr))
            print(date)
            print(finalstr)
            oldstr = finalstr
    else:
        string4 = string3
        string5 = string4.replace("\\n", " ")
        string6 = string5.replace('\\', "\n")
        finalstr = "[ " + string6
        if oldstr != finalstr:
            client.send_message(announcementChannel, '@everyone\n' + str(date) + '\n' + str(finalstr))
            print(date)
            print(finalstr)
            oldstr = finalstr 
    
@client.event
#Print-out to CMD who you're logged in as
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
    global announcementChannel
    announcementChannel = client.servers[0]
    
    for x in client.get_all_channels():
        print("Checking " + x.name)
        if x.name == 'bot_notifications':
            announcementChannel = x
            print("Set announcementChannel successfully to " + x.name)
            break
    findEQ()

@client.event
#Reply to users who say stuff
def on_message(message):
    
    if message.content.lower() == '!help':
        if not message.channel.name.startswith('eq'):
            client.send_message(message.channel, 'Hello {}'.format(message.author.mention() + '\nI am the bot that alerts you about the upcoming emergency quests in Ship 02(WIP).\n Here are the list of commands you are able to use: \n!help\n!eq\n!fuckyou\n!addme\n!removeme\n\n@MANAGERS\n!startmpa\n!removempa\n!addplayer *PLAYERNAME*\n!removeplayer *PLAYERNAME*'))

    elif message.content.lower() == '!fuckyou':
        if not message.channel.name.startswith('eq'):
            client.send_message(message.channel, 'Fuck you {}!'.format(message.author.mention()) + '～:hearts:')
        
    elif message.content.lower() == '!startmpa':
        if message.channel.name.startswith('eq'):
            if not message.channel.name in EQTest:
                if message.author.roles[1].permissions.can_manage_channels:
                    EQTest[message.channel.name] = list()
                    client.send_message(message.channel, 'Starting MPA on {}'.format(message.channel.name))
                else: 
                    client.send_message(message.channel, 'You are not a manager.')
            else:
                generateList(message, 'There is already an MPA to keep track of in this channel.')
        else:
            client.send_message(message.channel, 'You are unable to start a MPA on a non-EQ channel')

    elif message.content.lower() == '!addme':
        if message.channel.name.startswith('eq'):
            if message.channel.name in EQTest:
                if len(EQTest[message.channel.name]) <= 11:
                    if not(message.author in EQTest[message.channel.name]):
                        if message.author.id == message.server.owner.id:
                            EQTest[message.channel.name].insert(0, message.author)
                            generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                        else:
                            EQTest[message.channel.name].append(message.author)
                            generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                    else:
                        generateList(message, "You are already in the MPA")
                else:
                    generateList(message, 'The MPA is now full.')
            else:
                client.send_message(message.channel, 'A manager did not start the MPA yet')

    elif message.content.lower() == '!removeme':
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQTest:
                    if (message.author in EQTest[message.channel.name]):
                        EQTest[message.channel.name].remove(message.author)
                        generateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                    else:
                     generateList(message, 'You were not in the MPA list in the first place.')
					 
    elif message.content.lower() == '!removempa':
        if message.author.roles[1].permissions.can_manage_channels:
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQTest:
                    try:
                        del EQTest[message.channel.name]
                        client.send_message(message.channel, 'MPA {} is deleted.'.format(message.channel.name))
                        client.delete_channel(message.channel)
                    except KeyError:
                        pass
                else:
                    client.send_message(message.channel, 'There is no existing MPA to delete.')
            else:
                client.send_message(message.channel, 'There is no existing MPA to delete in a non EQ channel.')
        else:
                generateList(message, 'You are not a manager.')
				
    elif message.content.lower().startswith('!removeplayer '):
        if message.author.roles[1].permissions.can_manage_channels:
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQTest:
                    if len(EQTest[message.channel.name]):

                            userstr = message.content
                            userstr = userstr.replace("!removeplayer ", "")
                            for index in range(len(EQTest[message.channel.name])):
                                appended = False
                                if userstr == EQTest[message.channel.name][index].name:
                                    EQTest[message.channel.name][index] = userstr
                                    EQTest[message.channel.name].remove(userstr)
                                    userstr = userstr
                                    generateList(message, '*Removed {} from the MPA list*'.format(userstr))
                                    appended = True
                                    break
                            if not appended:    
                                generateList(message, "Player {} does not exist in the MPA list".format(userstr))
                    else:
                        client.send_message(message.channel, "There are no players in the MPA.")
                else:
                    client.send_message(message.channel, 'There is no MPA.')
            else:
                client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
        else:
            generateList(message, "You don't have permissions to use this command")

    elif message.content.lower().startswith('!addplayer'):
        if message.author.roles[1].permissions.can_manage_channels:
            userstr = ''
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQTest:
                        if len(EQTest[message.channel.name]) <= 11:
                            userstr = message.content
                            userstr = userstr.replace("!addplayer", "")
                            userstr = userstr.replace(" ", "")
                            if userstr == "":
                                client.send_message(message.channel, "You can't add nobody")
                            else:
                                EQTest[message.channel.name].append(FakeMember(userstr))
                                generateList(message, '*Added {} to the MPA list*'.format(userstr))
                        else:
                            client.send_message(message.channel, 'The MPA is now full.')
                else:
                    client.send_message(message.channel, 'There is no MPA.')
            else:
                client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
        else:
            client.send_message(message.channel, "You don't have permissions to use this command")
        
    elif message.content.lower() == '!eq':
        if not message.channel.name.startswith('eq'):
            client.send_message(message.channel, date + '\n' + finalstr)

    elif message.content.lower() == '!startparse':
        if not message.channel.name.startswith('eq'):
            if message.author.id == enfoniusid:
                    findEQ()
                    #DEBUG client.send_message(message.channel, 'begin parse')

    elif message.content.lower() == '!id':
        if not message.channel.name.startswith('eq'):
            client.send_message(message.channel, message.author.id)

    elif message.content.lower() == 'test':
        if not message.channel.name.startswith('eq'):
            letters = ['A', 'B', 'C', 'D', 'F']
            suffixes = ['+', '', '-']
            client.send_message(message.channel, letters[randint(0, 4)] + suffixes[randint(0,2)])

    #DELETE ALL THE MESSAGES THAT AREN'T THE BOT'S IN THE EQ CHANNEL
    if message.channel.name.startswith('eq'):
        if message.author.id != decisionbotid:
            client.delete_message(message)


@client.event
#when a member joins the server, welcome the person.
def on_member_join(member):
    server = member.server
    client.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention(), server))

@client.event
def on_channel_create(channel):
    if channel.name.startswith('eq'):
        client.send_message(channel, '!startmpa')

client.run()

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

url = 'http://pso2emq.flyergo.eu/api/v2'
values = {'s':'basics','sumbit':'search'}
data = urllib.parse.urlencode(values)
ship1substr = 'Ship01:'
string1 = "[ "
string2 = '"},'
EST = Zone(-5,False,'EST')
JST = Zone(9,False,'JST')
oldstr = ''
finalstr = ''
date = ''
EQDict = {}
IDDict = {}
EQTest = {}

#password in infos.txt
fp_infos = open("infos.txt", "r")
infos = fp_infos.read()
fp_infos.close()
client = discord.Client()
client.login('snakeofthefestival@gmail.com', infos)
parsestarted = True

def generateList(message, inputstring):
    pCount = 1
    playerlist = ''
    for player in EQDict[message.channel.name]:
        playerlist += (str(pCount) + ". " + player + '\n')
        pCount+=1
        
    while pCount < 13:
        
        playerlist += (str(pCount) + ".\n")
        pCount+=1
        
#debug method
def testgenerateList(message, inputstring):
    pCount = 1
    playerlist = ''
    for member in EQTest[message.channel.name]:
        playerlist += (str(pCount) + ". " + member.name + '\n')
        pCount+=1
        
    while pCount < 13:
        playerlist += (str(pCount) + ".\n")
        pCount+=1
        
    client.send_message(message.channel, playerlist + inputstring)

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

def parse_eq():
    global oldstr
    global finalstr
    global date
    
    threading.Timer(10, findEQ).start()
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
                client.send_message(client.servers[0], str(date) + '\n' + str(noeqstr))
                print(date)
                print(noeqstr)
                oldstr = finalstr
        elif oldstr != finalstr:
            client.send_message(client.servers[0], '@everyone\n' + str(date) + '\n' + str(finalstr))
            print(date)
            print(finalstr)
            oldstr = finalstr
    else:
        string4 = string3
        string5 = string4.replace("\\n", " ")
        string6 = string5.replace('\\', "\n")
        finalstr = "[ " + string6
        if oldstr != finalstr:
            client.send_message(client.servers[0], '@everyone\n' + str(date) + '\n' + str(finalstr))
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

@client.event
#Reply to users who say stuff
def on_message(message):
    # we do not want the bot to reply to itself
    #if message.author == client.user:
        #return
    
    if message.content.lower() == '!help':
        client.send_message(message.channel, 'Hello {}'.format(message.author.mention() + '\nI am the bot that alerts you about the upcoming emergency quests in Ship 02(WIP).\n Here are the list of commands you are able to use: \n!help\n!fuckyou\n!addme\n!removeme\n!mpalist\n\n@MANAGERS\n!startmpa\n!removempa'))

    elif message.content.lower() == '!fuckyou':
        client.send_message(message.channel, 'Fuck you {}!'.format(message.author.mention()) + ':hearts:')

    elif message.content.lower() == '!startmpa':
        if message.channel.name.startswith('eq'):
            if message.author.roles[1].permissions.can_manage_channels:
                EQDict[message.channel.name] = set()
                IDDict[message.channel.name] = set()
                client.send_message(message.channel, 'Starting MPA on {}'.format(message.channel.name))
                client.delete_message(message)
            else:
                client.send_message(message.channel, 'You are not a manager.')
        else:
            client.send_message(message.channel, 'You are unable to start a MPA on a non-EQ channel')

    elif message.content.lower() == '!addme':
        if message.channel.name.startswith('eq'):
            if message.channel.name in EQDict:
                if len(EQDict[message.channel.name]) <= 11:
                    if (message.author.id in IDDict[message.channel.name]) == False:
                        EQDict[message.channel.name].add(message.author.name)
                        IDDict[message.channel.name].add(message.author.id)
                        #client.send_message(message.channel, 'Adding {} to the MPA list'.format(message.author.name))
                        generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                    else:
                        client.send_message(message.channel, "You are already in the MPA")
                else:
                    client.send_message(message.channel, 'The MPA is now full.')
            else:
                client.send_message(message.channel, 'A manager did not start the MPA yet')

    elif message.content.lower() == '!removeme':
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQDict:
                    if message.author.id in IDDict[message.channel.name]:
                        if message.author.name in EQDict[message.channel.name]:
                            EQDict[message.channel.name].remove(message.author.name)
                            IDDict[message.channel.name].remove(message.author.id)
                            #client.send_message(message.channel, 'Removed {} from the MPA list.'.format(message.author.name))
                            generateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                        else:
                            client.send_message(message.channel, 'Your current name is not in the MPA list. Change it back.')
                    else:
                        client.send_message(message.channel, 'You were not in the MPA list in the first place.')
                

    elif message.content.lower() == '!removempa':
        if message.author.roles[1].permissions.can_manage_channels:
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQDict:
                    try:
                        del EQDict[message.channel.name]
                        client.send_message(message.channel, 'MPA {} is deleted.'.format(message.channel.name))
                        client.delete_channel(message.channel)
                    except KeyError:
                        pass
                else:
                    client.send_message(message.channel, 'There is no existing MPA to delete.')
            else:
                client.send_message(message.channel, 'There is no existing MPA to delete in a non EQ channel.')
        else:
                client.send_message(message.channel, 'You are not a manager.')

    elif message.content.lower() == '!mpalist':
        if message.channel.name.startswith('eq'):
            if message.channel.name in EQDict:
                if len(EQDict[message.channel.name]):
                    #pCount = 1
                    #playerlist = ''
                    #for player in EQDict[message.channel.name]:
                        #playerlist += (str(pCount) + ". " + player + '\n')
                        #pCount+=1
                    generateList(message, "")
                    client.send_message(message.channel, playerlist)
                else:
                    client.send_message(message.channel, 'There are no players in the MPA.')
            else:
                client.send_message(message.channel, 'There is no MPA.')
        else:
            client.send_message(message.channel, 'This is a non EQ channel.')

    elif message.content.lower() == '!eq':
        client.send_message(message.channel, date + '\n' + finalstr)

    elif message.content.lower() == '!startparse':
        global parsestarted
        if message.author.id == '125045788958130177':
            if parsestarted == True:
                parsestarted = False
                parse_eq()
                #DEBUG client.send_message(message.channel, 'begin parse')

    elif message.content.lower() == '!id':
            client.send_message(message.channel, message.author.id)

    elif message.content.lower() == 'test':
        letters = ['A', 'B', 'C', 'D', 'F']
        suffixes = ['+', '', '-']
        client.send_message(message.channel, letters[randint(0, 4)] + suffixes[randint(0,2)])

    elif message.content.lower().startswith('!removeplayer '):
        if message.author.roles[1].permissions.can_manage_channels:
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQDict:
                    if len(EQDict[message.channel.name]):

                            userstr = message.content
                            userstr = userstr.replace("!removeplayer ", "")
                            #userstr = userstr.replace(" ", "")
                            if userstr in EQDict[message.channel.name]:
                                EQDict[message.channel.name].remove(userstr)
                                userstr = userstr
                                generateList(message, '*Removed {} from the MPA list*'.format(userstr))
                            else:
                                client.send_message(message.channel, "Player {} does not exist in the MPA list".format(userstr))
                    else:
                        client.send_message(message.channel, "There are no players in the MPA.")
                else:
                    client.send_message(message.channel, 'There is no MPA.')
            else:
                client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
        else:
            client.send_message(message.channel, "You don't have permissions to use this command")

    elif message.content.lower().startswith('!addplayer'):
        if message.author.roles[1].permissions.can_manage_channels:
            userstr = ''
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQDict:
                        if len(EQDict[message.channel.name]) <= 11:
                            userstr = message.content
                            userstr = userstr.replace("!addplayer", "")
                            userstr = userstr.replace(" ", "")
                            if userstr == "":
                                client.send_message(message.channel, "You can't add nobody")
                            else:
                                EQDict[message.channel.name].add(userstr)
                                generateList(message, '*Added {} to the MPA list*'.format(userstr))
                        else:
                            client.send_message(message.channel, 'The MPA is now full.')
                else:
                    client.send_message(message.channel, 'There is no MPA.')
            else:
                client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
        else:
            client.send_message(message.channel, "You don't have permissions to use this command")

    #debug method
    elif message.content.lower() == '!teststartmpa':
        if message.channel.name.startswith('eq'):
            if message.author.roles[1].permissions.can_manage_channels:
                EQTest[message.channel.name] = list()
                #IDDict[message.channel.name] = set()
                client.send_message(message.channel, 'Starting MPA on {}'.format(message.channel.name))
                client.delete_message(message)
            else:
                client.send_message(message.channel, 'You are not a manager.')
        else:
            client.send_message(message.channel, 'You are unable to start a MPA on a non-EQ channel')
    #debug method
    elif message.content.lower() == '!testaddme':
        if message.channel.name.startswith('eq'):
            if message.channel.name in EQTest:
                if len(EQTest[message.channel.name]) <= 11:
                    if (message.author in EQTest[message.channel.name]) == False:
                        if message.author.id == '125045788958130177':
                            EQTest[message.channel.name].insert(12, message.author)
                            testgenerateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                        else:
                            EQTest[message.channel.name].append(message.author)
                            testgenerateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                    else:
                        client.send_message(message.channel, "You are already in the MPA")
                else:
                    client.send_message(message.channel, 'The MPA is now full.')
            else:
                client.send_message(message.channel, 'A manager did not start the MPA yet')

    elif message.content.lower() == '!testremoveme':
            if message.channel.name.startswith('eq'):
                if message.channel.name in EQTest:
                    if (message.author in EQTest[message.channel.name]):
                        EQTest[message.channel.name].remove(message.author)
                        testgenerateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                    else:
                     client.send_message(message.channel, 'You were not in the MPA list in the first place.')

    if message.channel.name.startswith('eq'):
        if message.author.id != '130739227351711744':
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

import discord
import asyncio
import urllib.request
import urllib.parse
import re
import cleverbot
from datetime import datetime,tzinfo,timedelta
from random import randint

cleverbot_client = cleverbot.Cleverbot()
 
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
 
class PlaceHolder():
    def __init__(self, name):
        self.name = name
 
decisionbotid = '134663393586970624' #decisionbot
ITid = '125045788958130177'#Replace this string with your own ID.
EQDict = {}
IDDict = {}
EQTest = {}
SubDict = {}
EQPostDict = {}
appended = False
EST = Zone(-5,False,'EST') #Based on what timezone the majority of your team is in, you can change the format of the EST object.
JST = Zone(9,False,'JST')
date = ''
strCheck = ''
entireNotice = ''

client = discord.Client()
 
#Generates the list that the bot will be posting everytime the list updates. The format is as follows:
#Party 1
#1.
#2.
#3.
#4.
#Party 2
#1.
#2.
#3.
#4.
#Party 3
#1.
#2.
#3.
#4.
@asyncio.coroutine
def generateList(message, inputstring):
    pCount = 1
    nCount = 1
    sCount = 1
    mpaCount = 1
    playerlist = 'MPA List:\n'
    for member in EQTest[message.channel.name]:
        if nCount == 1:
            playerlist += ('Party ' + str(mpaCount) + '\n')
            mpaCount += 1
        playerlist += (str(nCount) + ". " + member.name + '\n')
        pCount+=1
        nCount+=1
        if nCount == 5:
            playerlist += ('\n')
            nCount = 1
       
    while pCount < 13:
        if nCount == 1:
            playerlist += ('Party ' + str(mpaCount) + '\n')
            mpaCount += 1
        playerlist += (str(nCount) + ".\n")
        pCount+=1
        nCount +=1
        if nCount == 5:
            playerlist += ('\n')
            nCount = 1

    if len(SubDict[message.channel.name]) > 0:
        playerlist += ('\nReserve List:\n')
        for member in SubDict[message.channel.name]:
            playerlist += (str(sCount) + ". " + member.name + '\n')
            sCount += 1  
    try:
        yield from client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring)
    except:
        print('posting first list')
        EQPostDict[message.channel.name] = yield from client.send_message(message.channel, playerlist + inputstring)
   
#EQ parser method
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

#EQ parser method. Goes into flyergo's website and parses out the latest EQ that is updated there.

@asyncio.coroutine
def findEQ2():
    global strCheck
    global entireNotice
    yield from client.wait_until_ready()
    date = ('*' + str(datetime.now(EST).strftime('%H:%M %Z')) + '\n' + str(datetime.now(JST).strftime('%H:%M %Z')) + '*')
    servers = list(client.servers)
    channel = servers[0]
    
    print("default channel set to announcement. check other channels pls")
    for x in client.get_all_channels():
        print("Checking " + x.name)
        if x.name == 'bot_notifications':
            channel = x
            print("Set announcementChannel successfully to " + x.name)
            break
        
    while not client.is_closed:
        url = 'http://pso2emq.flyergo.eu/api/v2'
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        respData = resp.read()

        date = ('*' + str(datetime.now(EST).strftime('%H:%M %Z')) + '\n' + str(datetime.now(JST).strftime('%H:%M %Z')) + '*')
        timeOfNotice = find_between(str(respData), 'text":"', '\\n')
        timeOfNotice = timeOfNotice.replace('\\', '')
        entireNotice = find_between(str(respData), '[ ', '"}')

        if 'Ship01:' in entireNotice:
            entireNotice = find_between(entireNotice, 'Ship02', 'Ship03')
            entireNotice = entireNotice.replace('\\n', '')
            entireNotice = entireNotice.replace('\\', '\n')
            entireNotice = timeOfNotice + '\nShip02' + entireNotice

            if '\nShip02: -' in entireNotice:
                if strCheck != entireNotice:
                    noEQStr = '\nThere is no EQ going on in Ship02 at the given hour.'
                    noEQStr = timeOfNotice + noEQStr
                    yield from client.send_message(channel, str(date) + '\n' + noEQStr)
                    print(str(date) + '\n' + noEQStr)
                    strCheck = entireNotice
            elif strCheck != entireNotice:
                yield from client.send_message(channel, '@everyone\n' + str(date) + '\n' + entireNotice)
                print('@everyone\n' + str(date) + entireNotice)
                strCheck = entireNotice
        else:
            entireNotice = entireNotice.replace('\\n', '')
            entireNotice = entireNotice.replace('\\', '\n')
            entireNotice = "[ " + entireNotice
            if strCheck !=  entireNotice:
                yield from client.send_message(channel, '@everyone\n' + str(date) + '\n' + entireNotice)
                print('@everyone\n' + str(date) + entireNotice)
                strCheck = entireNotice
        yield from asyncio.sleep(300) # task runs every 300 seconds/5 minutes
            
@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

 
@client.event
@asyncio.coroutine
##  GENERAL COMMANDS ##
def on_message(message):
    global appended
    if message.content.startswith(client.user.mention):
        if not message.channel.name.startswith('mpa'):
            print('caught message')
            question = message.content.replace("@John Cena ", '') 
            answer = cleverbot_client.ask(question)
            yield from client.send_message(message.channel, answer)
            
    elif message.content.lower() == 'test':
            if not message.channel.name.startswith('mpa'):
                letters = ['A', 'B', 'C', 'D', 'F']
                suffixes = ['+', '', '-']
                yield from client.send_message(message.channel, letters[randint(0, 4)] + suffixes[randint(0,2)])
     
    elif message.content.lower() == 'and his name is':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, ':trumpet::trumpet::trumpet::trumpet:\n  **JOHN CENA**\n:trumpet::trumpet::trumpet::trumpet:')
    
    if message.content.startswith('!'):
        if message.content.lower() == ('!help'):
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'Hello {}'.format(message.author.mention) + '\nMy name is John Cena. I tell you about upcoming EQs and organize MPAs. You can use these following commands:\n!hello\n!help\n!addme\n!removeme')

        elif message.content.lower() == '!hello':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'Hello {}.'.format(message.author.mention))
     
        elif message.content.lower() == '!fuckyou':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'Fuck you too, {}!'.format(message.author.mention))
               
        elif message.content.lower() == '!eq':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, date + '\n' + finalstr)
                
        ## MPA TRACKER COMMANDS
     
        #Starts the MPA on the current eq channel. Places the channel name into a dictionary and sets it to be a list. Then fills the list up with 12 placeholder objects.
               
        elif message.content.lower() == '!startmpa':
            if message.channel.name.startswith('mpa'):
                yield from client.delete_message(message)
                if not message.channel.name in EQTest:
                    if message.author.roles[1].permissions.manage_channels:
                        EQTest[message.channel.name] = list()
                        SubDict[message.channel.name] = list()
                        for index in range(12):
                            EQTest[message.channel.name].append(PlaceHolder(""))
                        yield from generateList(message, 'Starting MPA on {}'.format(message.channel.name))
                    else:
                        yield from client.send_message(message.channel, 'You are not a manager.')
                else:
                    yield from generateList(message, 'There is already an MPA to keep track of in this channel.')
            else:
                yield from client.send_message(message.channel, 'You are unable to start a MPA on a non-EQ channel')
     
        #Removes the MPA on the current eq channel as well as deletes it. USE THIS TO CLOSE YOUR CHANNELS SO YOUR MEMORY SPACE ISN'T HOGGED UP BY THIS TINY PROGRAM.
                                 
        elif message.content.lower() == '!removempa':
            if message.author.roles[1].permissions.manage_channels:
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        try:
                            del EQTest[message.channel.name]
                            ##yield from client.send_message(message.channel, 'MPA {} is deleted.'.format(message.channel.name))
                            yield from client.delete_channel(message.channel)
                        except KeyError:
                            pass
                    else:
                        yield from client.send_message(message.channel, 'There is no existing MPA to delete.')
                else:
                    yield from client.send_message(message.channel, 'There is no existing MPA to delete in a non EQ channel.')
            else:
                yield from generateList(message, 'You are not a manager.')
                   
     
     
            #Adds a player into the MPA list on the current eq channel. Checks for a placeholder object to remove and inserts the user's user object into the list.
        elif message.content.lower() == '!addme':
            if message.channel.name.startswith('mpa'):
                if message.channel.name in EQTest:
                    for member in EQTest[message.channel.name]:
                        if isinstance(member, PlaceHolder):
                            if not(message.author in EQTest[message.channel.name]):
                                if message.author.id == message.server.owner.id:
                                    EQTest[message.channel.name].pop(0)
                                    EQTest[message.channel.name].insert(0, message.author)
                                    yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                    appended = True
                                    break
     
                                elif message.author.roles[1].permissions.manage_channels:
                                    if isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                        EQTest[message.channel.name].pop(4)
                                        EQTest[message.channel.name].insert(4, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                        EQTest[message.channel.name].pop(8)
                                        EQTest[message.channel.name].insert(8, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    else:
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                else:
                                    if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                        EQTest[message.channel.name].pop(1)
                                        EQTest[message.channel.name].insert(1, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                        EQTest[message.channel.name].pop(2)
                                        EQTest[message.channel.name].insert(2, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                        EQTest[message.channel.name].pop(3)
                                        EQTest[message.channel.name].insert(3, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                        EQTest[message.channel.name].pop(5)
                                        EQTest[message.channel.name].insert(5, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                        EQTest[message.channel.name].pop(6)
                                        EQTest[message.channel.name].insert(6, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                        EQTest[message.channel.name].pop(7)
                                        EQTest[message.channel.name].insert(7, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                        EQTest[message.channel.name].pop(9)
                                        EQTest[message.channel.name].insert(9, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                        EQTest[message.channel.name].pop(10)
                                        EQTest[message.channel.name].insert(10, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                        EQTest[message.channel.name].pop(11)
                                        EQTest[message.channel.name].insert(11, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                        EQTest[message.channel.name].pop(4)
                                        EQTest[message.channel.name].insert(4, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                        EQTest[message.channel.name].pop(8)
                                        EQTest[message.channel.name].insert(8, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                        EQTest[message.channel.name].pop(0)
                                        EQTest[message.channel.name].insert(0, message.author)
                                        yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                            else:
                                yield from generateList(message, "*You are already in the MPA*")
                                break
                    if not appended:
                        if not(message.author in EQTest[message.channel.name]): 
                            yield from generateList(message, "*The MPA is full. Adding to reserve list.*")
                            if not(message.author in SubDict[message.channel.name]):
                                SubDict[message.channel.name].append(message.author)
                                yield from generateList(message, '*Added {} to the Reserve list*'.format(message.author.name))
                            else:
                                yield from generateList(message, "*You are already in the Reserve List*")
                        else:
                            yield from generateList(message, "*You are already in the MPA*")
                    appended = False                                
                else:
                    yield from client.send_message(message.channel, 'A manager did not start the MPA yet')
            else:
                yield from client.delete_message(message)
               
        #Adds a string/name of a player that the Manager wants into the MPA list.      
        elif message.content.lower().startswith('!add'):
            if message.author.roles[1].permissions.manage_channels:
                userstr = ''
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!add", "")
                        userstr = userstr.replace(" ", "")
                        if userstr == "":
                            yield from generateList(message, "You can't add nobody")
                            appended = True
                        else:
                            for member in EQTest[message.channel.name]:
                                if isinstance(member, PlaceHolder):
                                    if not(userstr in EQTest[message.channel.name]):
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                        if not appended:
                            yield from generateList(message, "*The MPA is full. Adding to reserve list.*")
                            SubDict[message.channel.name].append(FakeMember(userstr))
                            yield from generateList(message, '*Added {} to the Reserve list*'.format(userstr))
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA.')
                else:
                    yield from client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                yield from client.send_message(message.channel, "You don't have permissions to use this command")
            appended = False
     
        #Removes the user object from the MPA list.
        elif message.content.lower() == '!removeme':
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        if (message.author in EQTest[message.channel.name]):
                            index = EQTest[message.channel.name].index(message.author)
                            EQTest[message.channel.name].pop(index)
                            EQTest[message.channel.name].insert(index, PlaceHolder(''))
                            yield from generateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                            if len(SubDict[message.channel.name]) > 0:
                                EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                yield from generateList(message, '*Removed {} from the MPA list and added {}*'.format(message.author.name, EQTest[message.channel.name][index].name))
                        elif (message.author in SubDict[message.channel.name]):
                            SubDict[message.channel.name].remove(message.author)
                            yield from generateList(message, '*Removed {} from the Reserve list*'.format(message.author.name))
                        else:
                         yield from generateList(message, 'You were not in the MPA list in the first place.')
     
        #Removes the player object that matches the input string that is given.
        elif message.content.lower().startswith('!remove '):
            if message.author.roles[1].permissions.manage_channels:
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        if len(EQTest[message.channel.name]):
                                userstr = message.content
                                userstr = userstr.replace("!remove ", "")
                                for index in range(len(EQTest[message.channel.name])):
                                    appended = False
                                    if userstr == EQTest[message.channel.name][index].name:
                                        EQTest[message.channel.name][index] = userstr
                                        EQTest[message.channel.name].remove(userstr)
                                        EQTest[message.channel.name].insert(index, PlaceHolder(''))
                                        userstr = userstr
                                        yield from generateList(message, '*Removed {} from the MPA list*'.format(userstr))
                                        if len(SubDict[message.channel.name]) > 0:
                                            EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                            yield from generateList(message, '*Removed {} from the MPA list and added {}*'.format(userstr, EQTest[message.channel.name][index].name))
                                        appended = True
                                        break
                                if not appended:
                                    for index in range(len(SubDict[message.channel.name])):
                                        appended = False
                                        if userstr == SubDict[message.channel.name][index].name:
                                            SubDict[message.channel.name][index] = userstr
                                            SubDict[message.channel.name].remove(userstr)
                                            userstr = userstr
                                            yield from generateList(message, '*Removed {} from the Reserve list*'.format(userstr))
                                            appended = True
                                            break
                                if not appended:    
                                    yield from generateList(message, "Player {} does not exist in the MPA list".format(userstr))
                        else:
                            yield from client.send_message(message.channel, "There are no players in the MPA.")
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA.')
                else:
                    yield from client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                yield from generateList(message, "You don't have permissions to use this command")
     
        if message.channel.name.startswith('mpa'):
            if message.author.id != decisionbotid:
                if message.content.lower() != '!removempa':
                    yield from client.delete_message(message)
                    
@client.event
@asyncio.coroutine
#when a member joins the server, welcome the person.
def on_member_join(member):
    server = member.server
    yield from client.send_message(server, 'Welcome {0} to {1.name}! Please use !help to figure out how I work'.format(member.mention, server))
 
@client.event
@asyncio.coroutine
#Automiatically starts an MPA the moment the EQ channel is created.
def on_channel_create(channel):
    if channel.name.startswith('mpa'):
        yield from client.send_message(channel, '!startmpa')


client.loop.create_task(findEQ2())
client.run(token)

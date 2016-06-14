#!/usr/bin/env python3

# imports
from blessed import Terminal
import sys
import requests
import configparser
from os import getenv
from os import path
from time import sleep, time
import logging


def inputAction(action):
    payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.ExecuteAction","params":{"action":"'+action+'"}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    return r.json()


def updateAV(library):
    payload = '{"id": "1", "jsonrpc": "2.0", "method": "'+library+'.Scan"}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)


def sendText(text):
    payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.SendText","params":{"text":"'+text+'"}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)


def getWindowID():
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "GUI.GetProperties", "params":{"properties":["currentwindow"]} }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)
    return r.json()['result']['currentwindow']['id']



def getProperties(playerid):
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetProperties", "params":{"playerid":'+playerid+',"properties":["time","totaltime","percentage","type","speed"]} }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)
    return r.json()



def getPlayerID():
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetActivePlayers" }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    try:
        return str(r.json()['result'][0]['playerid'])
    except (IndexError):
        return False


def getTitle(playerid):
    try:
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetItem", "params":{"playerid":'+playerid+',"properties":["title","artist","showtitle"]} }'
        r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
        title = r.json()['result']['item']['title']
        if 'showtitle' not in r.json()['result']['item']:
            artist = r.json()['result']['item']['artist'][0]
        else:
            artist = r.json()['result']['item']['showtitle']
        return title,artist
    except:
        return "null","null"


def getTimes(curProperties):
    try:
        if curProperties['result']['totaltime']['hours'] == 0:
            curTime =  "{}:{:02d}".format(curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
            totalTime = "{}:{:02d}".format(curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
        else:
            curTime =  "{}:{}:{:02d}".format(curProperties['result']['time']['hours'],curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
            totalTime = "{}:{}:{:02d}".format(curProperties['result']['totaltime']['hours'],curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
        times = "{}/{}".format(curTime,totalTime)
    except:
        return "00:00/00:00"
    return times


def getRecentEps():
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "VideoLibrary.GetRecentlyAddedEpisodes" }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    try:
        return r.json()
    except (IndexError):
        return False

def getPlaylistItem():
    try:
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Playlist.GetItems", "params":{"playlistid":0,"properties":["title"]} }'
        r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
        toReturn = r.json()['result']['items']
    except:
        try:
            payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Playlist.GetItems", "params":{"playlistid":1, "properties":["title"]} }'
            r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
            toReturn = r.json()['result']['items']
        except:
            payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Playlist.GetItems", "params":{"playlistid":2, "properties":["title"]} }'
            r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
            toReturn = r.json()['result']['items']
    return toReturn

def getEpDetails(episodeid):
    episodeid = str(episodeid)
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params":{"episodeid":'+episodeid+',"properties":["file"]} }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    return r.json()['result']['episodedetails']

def openFile(targetFile):
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.Open", "params":{"item":{"file":"'+targetFile+'"}}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    return r.json()

def keyParse(keyIn):
    if keyIn == 'q':
        print(t.exit_fullscreen())
        sys.exit(0)

    elif keyIn.name == 'KEY_F1':
        print(t.exit_fullscreen())
        helpView()
    
    elif keyIn.name == 'KEY_F5':
        with t.location(y=6):
            print(t.clear())

    elif keyIn.name == 'KEY_F2':
        recentEpsList = getRecentEps()['result']['episodes']
        recentEpsInfo = [ getEpDetails(x['episodeid']) for x in recentEpsList]
        recentEpsList = [ x['label'] for x in recentEpsInfo]
        selectionLabel,selectionIndex = menuView(recentEpsList,t)
        if selectionLabel != False and selectionIndex != False:
            openFile(recentEpsInfo[selectionIndex]['file'])

    # Actions
    elif keyIn.name == 'KEY_ESCAPE' or keyIn.name == "KEY_F11":
        inputAction("fullscreen")
    elif keyIn == ' ':
        inputAction("pause")
    elif keyIn == ']':
        inputAction("skipnext")
    elif keyIn == '[':
        inputAction("skipprevious")
    elif keyIn == 'x':
        inputAction("stop")

    elif keyIn == 'H':
        inputAction("back")
    elif keyIn == 'h':
        if getWindowID() == 12005 or getWindowID() == 12006:
            inputAction("stepback")
        inputAction("left")
    elif keyIn == 'l':
        if getWindowID() == 12005 or getWindowID() == 12006:
            inputAction("stepforward")
        inputAction("right")
    elif keyIn == 'k':
        inputAction("up")
    elif keyIn == 'j':
        inputAction("down")
    
    elif keyIn == 'c':
        inputAction("contextmenu")
    elif keyIn == 'i':
        inputAction("info")

    elif keyIn == '-':
        inputAction("volumedown")
    elif keyIn == '=':
        inputAction("volumeup")
    elif keyIn == '0':
        inputAction("mute")
    
    elif keyIn == 'u':
        updateAV("VideoLibrary")
    elif keyIn == 'U':
        updateAV("AudioLibrary")

    elif keyIn == 'u':
        updateAV("VideoLibrary")
    elif keyIn == 'U':
        updateAV("AudioLibrary")


    elif keyIn.name == 'KEY_ENTER':
        if getWindowID() != 10120:
            inputAction("select")
            inputAction("osd")
        else:
            inputAction("select")


def textPrompt(t):
    with t.location(x=0,y=5):
        print(t.bold_blue("▒"*(t.width//2)))
    with t.location(x=0,y=5):
        usrIn = input(t.bold_blue("Enter text: "))
    with t.location(x=0,y=5):
        print(" "*t.width)
    return usrIn


def nowPlayingView():
    print(t.enter_fullscreen(),t.clear())
    with t.location(y=0,x=0):
        print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))
    while True:
        with t.raw(): 
            keyIn = t.inkey(1)
            keyParse(keyIn)

        if int(time()) % 10 == 0:
            # "Flush" the padding areas and title every few seconds.
            # If the user resizes, stuff can get stuck in there as blessed doesn't redraw unless asked
            # print(t.clear())
            with t.location(y=0,x=0):
                print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))
            # If the user resizes stuff can get stuck in the buffer. 
            with t.location(y=1):
                print(t.center(""))
            with t.location(y=5):
                print(t.center(""))
            print(t.move(0,0))


        playerid = getPlayerID()
        if playerid != False:
            curProperties = getProperties(playerid)
            times = getTimes(curProperties)
            title,artist = getTitle(playerid)
            progPerct = curProperties['result']['percentage']/100
            progWidth = t.width - len(times)
            progBar = int(progPerct*progWidth)
            if displayPlaylist in ['true','True']:
                if int(time()) % 2 == 0:
                    try:
                        playlistView(title)
                    except:
                        pass


            with t.location(y=2):
                if artist != '':
                    print(t.center(t.bold(title) +" - {}".format(artist)))
                else: 
                    print(t.center(t.bold(title)))

            if curProperties['result']['speed'] == 0:
                with t.location(x=0, y=3):
                    print(t.center("[paused]"))
                with t.location(x=0, y=4):
                    print("─"*progBar+t.red("┃")+"─"*(progWidth - progBar-1)+times)

            else:
                with t.location(x=0, y=3):
                    print(t.center(" "))
                with t.location(x=0, y=4):
                    print(t.red("━"*progBar+"╉")+"─"*(progWidth - progBar-1)+times)

        else:
            with t.location(x=0, y=2):
                print(t.center(t.bold("Play something!")))

        if getWindowID() == 10103:
            sendText(textPrompt(t))


def playlistView(title):
    playlist = getPlaylistItem()
    playlistItems = [ x['title'] for x in playlist ]
    if len(playlistItems) > 1:
        if playlistItems.index(title) > 2:
            # If we're a couple songs deep, We don't want to see the whole start of the playlist, just 2 before current
            playNum = playlistItems.index(title) - 2
            playlist = playlistItems[playNum:]
            # playlist = playlist[:playNum]
            # playlist = playlistItems

            # Make "entries" into the list so that we flush old entries when it scrolls up
            # for i in range(len(playlist)+6,t.height):
            #     playlist.append(" "*t.width)

            for i in playlist[:t.height-7]:
                with t.location(y=6+playlist.index(i)):
                    if i == title:
                        print(t.center(t.bold(t.white_on_black(i))))
                    else:
                        print(t.center(i))
        else:
            playlist = playlistItems
            # playlist = playlist[:playNum]
            # playlist = playlistItems

            # Make "entries" into the list so that we flush old entries when it scrolls up
            # for i in range(len(playlist)+6,t.height):
            #     playlist.append(" "*t.width)

            for i in playlist[:t.height-7]:
                with t.location(y=6+playlist.index(i)):
                    if i == title:
                        print(t.center(t.bold(i)))
                    else:
                        print(t.center(i))

def menuView(options,term):
    offset=2
    print(term.enter_fullscreen())
    print(term.move(offset-1,0))
    with term.location(0,0):
        print(term.bold(term.blue(term.center("Enter to select, q to cancel."))))
    while True:

        cursy,cursx = term.get_location()
        
        for i in range(0,len(options)):
            # Need to compensate for the way the cursor is show on the screen. Hence -1 -offset
            if cursy-1-offset == i:
                with term.location(y=i+offset):
                    print(term.center(term.white_on_black(term.bold(options[i]))))
            else:
                with term.location(y=i+offset):
                    print(term.center(options[i]))
        
        with term.raw():
            key = term.inkey(1)
            if key == "q":
                return False,False
            elif key.name == "KEY_UP" or key == 'k':
                print(term.move_up(),end="")
            elif key.name == "KEY_DOWN" or key == 'j':
                print(term.move_down(),end="")
            elif key.name == "KEY_ENTER" or key == ' ':
                print(term.exit_fullscreen())
                return options[cursy-1-offset],cursy-1-offset

def helpView():
    print(t.enter_fullscreen)
    with t.location(y=6):
        print(t.center("H h j k l : back left down up right"))
        print(t.center("[ ] space x : previous next pause stop"))
        print(t.center("c i - = 0 : context info voldown volup mute"))
        print(t.center("u U : Video Audio library update"))
        print(t.center("ESC : switch to/from media view"))
        print(t.center("F1 F2 F5 q : help recently added episodes clear quit"))
    while True:
        with t.raw(): 
            keyIn = t.inkey(1)
            if keyIn == 'q' or keyIn.name == 'KEY_F1' or keyIn.name == "KEY_ENTER":
                print(t.exit_fullscreen)
                print(t.clear)
                break


home = getenv("HOME")
config = configparser.ConfigParser() #initializing config parser object
config.read('{}/.kodiremote/kodiremote.ini'.format(home)) #sending config file to config parser object
kodiHost = config['settings']['host']
kodiPort = config['settings']['port']
displayPlaylist = config['settings']['playlist']
headers = {'Content-Type': 'application/json'}

try:
    args = sys.argv[1:]
    if len(args) == 0:
        t = Terminal()
        with t.hidden_cursor(): 
            nowPlayingView()

    elif len(args) >= 1:
        if 'h' in args or 'help' in args or '--help' in args or '-help' in args:
            print("Navigation is hjkl, H for back, enter to select. F1 for help screen.")
            print("Run on its own or in one-shot mode with input action arguments.")
            print("Useful ones include left,right,down,up,pause,skipnext,skipprevious.")
            print("You can find all valid input action arguments here:")
            print("http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action")
            recentEpsList = getRecentEps()['result']['episodes']
            recentEpsInfo = [ getEpDetails(x['episodeid']) for x in recentEpsList]
            recentEpsList = [ x['label'] for x in recentEpsInfo]
            t = Terminal()
            print(menuView(recentEpsList,t))
            print(recentEpsInfo)
        else:
            for i in args:
                print(inputAction(i))

except (OSError,ConnectionError):
    print(t.exit_fullscreen())
    print("Cannot connect to Kodi server. Is it running? Is your config file configured?")
    pass

#!/usr/bin/env python3

# imports
from blessed import Terminal
import sys
import requests
import configparser
from os import getenv
from os import path

home = getenv("HOME")
config = configparser.ConfigParser() #initializing config parser object
config.read('{}/.kodiremote/kodiremote.ini'.format(home)) #sending config file to config parser object
kodiHost = config['settings']['host']
kodiPort = config['settings']['port']
headers = {'Content-Type': 'application/json'}

def inputAction(action):
    payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.ExecuteAction","params":{"action":"'+action+'"}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)


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
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetItem", "params":{"playerid":'+playerid+',"properties":["title","artist","showtitle"]} }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    title = r.json()['result']['item']['title']
    if 'showtitle' not in r.json()['result']['item']:
        artist = r.json()['result']['item']['artist'][0]
    else:
        artist = r.json()['result']['item']['showtitle']
    return title,artist


def getTimes(curProperties):
    if curProperties['result']['totaltime']['hours'] == 0:
        curTime =  "{}:{:02d}".format(curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
        totalTime = "{}:{:02d}".format(curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
    else:
        curTime =  "{}:{}:{:02d}".format(curProperties['result']['time']['hours'],curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
        totalTime = "{}:{}:{:02d}".format(curProperties['result']['totaltime']['hours'],curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
    times = "{}/{}".format(curTime,totalTime)
    return times


def keyParse(keyIn):
    if keyIn == 'q':
        print(t.exit_fullscreen())
        sys.exit(0)

    elif keyIn.name == 'KEY_F1':
        with t.location(y=6):
            print(t.center("H h j k l : back left down up right"))
            print(t.center("[ ] space x : previous next pause stop"))
            print(t.center("c i - = 0 : context info voldown volup mute"))
            print(t.center("u U : Video Audio library update"))
            print(t.center("ESC : switch to/from media view"))
            print(t.center("F1 F2 q : help clear quit"))
    
    elif keyIn.name == 'KEY_F2':
        with t.location(y=6):
            print(t.clear())

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


try:
    t = Terminal()
    args = sys.argv[1:]
    print(t.enter_fullscreen(),t.clear())
    if len(args) == 0:
        while True:
            with t.location(y=0,x=0):
                print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))

            print(t.move(0,0))

            playerid = getPlayerID()

            if playerid != False:
                curProperties = getProperties(playerid)
                times = getTimes(curProperties)
                title,artist = getTitle(playerid)
                progPerct = curProperties['result']['percentage']/100
                progWidth = t.width - len(times)
                progBar = int(progPerct*progWidth)

                with t.location(x=0, y=2):
                    if artist != '':
                        print(t.center(t.bold(title) +" - {}".format(artist)))
                    else: 
                        print(t.center(t.bold(title)))

                if curProperties['result']['speed'] == 0:
                    with t.location(x=0, y=4):
                        print(t.white("━"*progBar+"┈"*(progWidth - progBar))+times)

                else:
                    with t.location(x=0, y=4):
                        print(t.red("━")*progBar+"┈"*(progWidth - progBar)+times)


            else:
                with t.location(x=0, y=2):
                    print(t.center(t.bold("Play something!")))

            if getWindowID() == 10103:
                sendText(textPrompt(t))

            with t.raw(): 
                keyIn = t.inkey(1)
                keyParse(keyIn)

    elif len(args) == 1:
        inputAction(args[0])

except (OSError,ConnectionError):
    print(t.exit_fullscreen())
    print("Cannot connect to Kodi server. Is it running? Is your config file configured?")
    pass

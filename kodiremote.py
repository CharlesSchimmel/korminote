#!/usr/bin/env python3

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
    try:
        artist = r.json()['result']['item']['showtitle']
    except:
        artist = r.json()['result']['item']['artist'][0]
    return title,artist

def getTimes(curProperties):
    if curProperties['result']['totaltime']['hours'] == 0:
        curTime =  "{}:{}".format(curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
        totalTime = "{}:{}".format(curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
    else:
        curTime =  "{}:{}:{}".format(curProperties['result']['time']['hours'],curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
        totalTime = "{}:{}:{}".format(curProperties['result']['totaltime']['hours'],curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
    return curTime,totalTime

try:
    t = Terminal()
    args = sys.argv[1:]
    print(t.enter_fullscreen(),t.clear(),t.center(t.bold_blue("Kodi Terminal Remote;F1 for help; q to quit")))
    print()

    if len(args) == 0:
        debug = False
        while True:
            playerid = getPlayerID()
            curProperties = getProperties(playerid)
            progPerct = curProperties['result']['percentage']/100
            progBar = int(progPerct*t.width)
            curTime,totalTime = getTimes(curProperties)
            title,artist = getTitle(playerid)
            if playerid != False:
                with t.location(0, 2):
                    print("{} - {}".format(title,artist))
                if curProperties['result']['speed'] == 0:
                    with t.location(0, 3):
                        print("paused - {}/{}".format(curTime,totalTime)," "*t.width)
                    with t.location(0,4):
                        print("━"*progBar," "*t.width)
                else:
                    with t.location(0, 3):
                        print("playing - {}/{}".format(curTime,totalTime)," "*t.width)
                    with t.location(0, 4):
                        print("━"*progBar+"┈"*(t.width - progBar))

            if getWindowID() == 10103:
                userIn = input(t.bold_blue("Enter text: "))
                sendText(userIn)

            with t.raw():
                keyIn = t.inkey(1)

                # Settings and stuff
                if debug == True:
                    print(keyIn.name, keyIn.code)
                    print(getWindowID())
                if keyIn == 'q':
                    break
                elif keyIn == 'd':
                    debug = not debug

                elif keyIn.name == 'KEY_F1':
                    print(t.center(t.bold_blue("Controls:")))
                    print(t.center("H h j k l : back left down up right"))
                    print(t.center("[ ] space x : previous next pause stop"))
                    print(t.center("c i - = 0 : context info voldown volup mute"))
                    print(t.center("u U : Video Audio library update"))
                    print(t.center("ESC : switch to/from media view"))
                    print(t.center("d q : debug quit"))

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

    elif len(args) == 1:
        inputAction(args[0])
except (OSError,ConnectionError):
    print("Cannot find Kodi server. Have you checked your config file?")
    pass

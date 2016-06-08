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

def inputAction(action):
    payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.ExecuteAction","params":{"action":'+'"{}"'.format(action)+'}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)

def sendText(text):
    payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.SendText","params":{"text":'+'"{}"'.format(text)+'}}'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)

def getWindowID():
    payload = '{ "id": "1", "jsonrpc": "2.0", "method": "GUI.GetProperties", "params":{"properties":["currentwindow"]} }'
    r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=headers)
    if r.status_code != 200:
        print(r.text)
    return r.json()['result']['currentwindow']['id']

try:
    t = Terminal()
    headers = {'Content-Type': 'application/json'}
    args = sys.argv[1:]

    if len(args) == 0:
        debug = False
        print(t.bold_blue("Kodi Terminal Remote; F1 for help; q to quit"))
        while True:
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
                    print(t.center("Vi Keybindings for navigation, all else default."))
                    print(t.center("d: debug"))
                    print(t.center("ESC: switch to/from video"))

                # Actions
                elif keyIn.name == 'KEY_ESCAPE':
                    inputAction("fullscreen")
                elif keyIn == ' ':
                    inputAction("pause")
                elif keyIn == ']':
                    inputAction("skipnext")
                elif keyIn == '[':
                    inputAction("skipprevious")
                elif keyIn == 'H':
                    inputAction("back")
                elif keyIn == 'h':
                    if getWindowID() == 12005:
                        inputAction("stepback")
                    inputAction("left")
                elif keyIn == 'l':
                    if getWindowID() == 12005:
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

                elif keyIn.name == 'KEY_ENTER':
                    if getWindowID() != 10120:
                        inputAction("select")
                        inputAction("osd")
                    else:
                        inputAction("select")

    elif len(args) == 1:
        inputAction(args[0])
except:
    pass

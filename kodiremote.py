#!/usr/bin/env python3

# imports
from blessed import Terminal
import sys
import configparser
from os import getenv
from os import path
from time import sleep, time
from KodiClient import Kodi
# import logging

class Views:
    
    def __init__(self):
        kodi = Kodi()

def keyParse(keyIn,windowID,kodi):
    if keyIn == 'q':
        print(t.exit_fullscreen())
        sys.exit(0)

    elif keyIn.name == 'KEY_F1':
        helpView()
    elif keyIn.name == 'KEY_F2':
        recentEpsMenu(kodi,t)
    elif keyIn.name == 'KEY_F5':
        with t.location(y=6):
            print(t.clear())

    elif keyIn == 'y':
        yturl = textPrompt(t,"Enter Youtube Url")
        if yturl != False:
            kodi.playYoutube(yturl)

    # Actions
    elif keyIn.name == 'KEY_ESCAPE' or keyIn.name == "KEY_F11":
        kodi.inputAction("fullscreen")
    elif keyIn == ' ':
        kodi.inputAction("pause")
    elif keyIn == ']':
        kodi.inputAction("skipnext")
    elif keyIn == '[':
        kodi.inputAction("skipprevious")
    elif keyIn == 'x':
        kodi.inputAction("stop")

    elif keyIn == 'H':
        kodi.inputAction("back")
    elif keyIn == 'h':
        if windowID == 12005 or windowID == 12006:
            kodi.inputAction("stepback")
        kodi.inputAction("left")
    elif keyIn == 'l':
        if windowID == 12005 or windowID == 12006:
            kodi.inputAction("stepforward")
        kodi.inputAction("right")
    elif keyIn == 'k':
        kodi.inputAction("up")
    elif keyIn == 'j':
        kodi.inputAction("down")
    
    elif keyIn == 'c':
        kodi.inputAction("contextmenu")
    elif keyIn == 'i':
        kodi.inputAction("info")

    elif keyIn == '-':
        kodi.inputAction("volumedown")
    elif keyIn == '=':
        kodi.inputAction("volumeup")
    elif keyIn == '0':
        kodi.inputAction("mute")
    
    elif keyIn == 'u':
        kodi.updateAVLibrary("VideoLibrary")
    elif keyIn == 'U':
        kodi.updateAVLibrary("AudioLibrary")

    elif keyIn.name == 'KEY_ENTER':
        if windowID != 10120:
            kodi.inputAction("select")
            kodi.inputAction("osd")
        else:
            kodi.inputAction("select")


def recentEpsMenu(kodi,t):
    recentEpsList = kodi.getRecentEps()
    if recentEpsList != False:
        selectionLabel,selectionIndex = menuView([ x['label'] for x in recentEpsList],t)
        if selectionLabel != False:
            kodi.openFile(recentEpsList[selectionIndex]['file'])
    else:
        with t.location(y=0):
            print(t.bold(t.center("No Recent Episodes")))

def textPrompt(t,prompt="Enter Text: "):
    with t.location(x=0,y=5):
        print(t.bold_blue("▒"*(t.width//2)))
    with t.location(x=0,y=5):
        usrIn = input(t.bold_blue(prompt))
    with t.location(x=0,y=5):
        print(" "*t.width)
    if usrIn != "":
        return usrIn
    else:
        return False


def nowPlayingView(kodi):
    print(t.enter_fullscreen(),t.clear())
    with t.location(y=0,x=0):
        print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))
    while True:

        print(t.move(0,0))

        playerid = kodi.getPlayerID()
        windowID = kodi.getWindowID()

        if windowID == 10103:
            kodi.sendText(textPrompt(t))

        with t.cbreak(): 
            keyIn = t.inkey(1)
            keyParse(keyIn,windowID,kodi)

        if int(time()) % 10 == 0:
            # "Flush" the padding areas and title every few seconds.
            # If the user resizes, stuff can get stuck in there as blessed doesn't redraw unless asked
            with t.location(y=0,x=0):
                print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))
            with t.location(y=1):
                print(t.center(""))
            with t.location(y=5):
                print(t.center(""))


        # If we get something for the playerid, something's playing.
        if playerid != False:
            curProperties = kodi.playerProperties(playerid)
            totalTime,curTime = kodi.getFormattedTimes(curProperties)

            times = "{}/{}".format(totalTime,curTime)
            title,artist = kodi.getTitle(playerid)

            progPerct = curProperties['result']['percentage']/100
            progWidth = t.width - len(times)
            progBar = int(progPerct*progWidth)

            if displayPlaylist.lower() in ['true','yes']:
                playlistModule(kodi,t,title,curProperties)

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


def playlistModule(kodi,t,title,curProperties):
    if int(time()) % 2 == 0:
        try:
            playlist = kodi.getPlaylistItems(curProperties)
            playlistItems = [ x['title'] for x in playlist ]
            if len(playlistItems) > 1:
                if playlistItems.index(title) > 2:
                    # If we're a couple songs deep, We don't want to see the whole start of the playlist, just 2 before current
                    playNum = playlistItems.index(title) - 2
                    playlist = playlistItems[playNum:]

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

                    # Make "entries" into the list so that we flush old entries when it scrolls up
                    # for i in range(len(playlist)+6,t.height):
                    #     playlist.append(" "*t.width)

                    for i in playlist[:t.height-7]:
                        with t.location(y=6+playlist.index(i)):
                            if i == title:
                                print(t.center(t.bold(i)))
                            else:
                                print(t.center(i))
        except:
            pass

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
        
        with term.cbreak():
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
        print(t.center("u U : Video,Audio library update"))
        print(t.center("y : open youtube url"))
        print(t.center("ESC : switch to/from media view"))
        print(t.center("F1 F2 F5 q : help recently added episodes clear quit"))
    while True:
        with t.cbreak(): 
            keyIn = t.inkey(1)
            if keyIn == 'q' or keyIn.name == 'KEY_F1' or keyIn.name == "KEY_ENTER":
                print(t.exit_fullscreen)
                print(t.clear)
                break


try:
    config = configparser.ConfigParser() #initializing config parser object
    config.read('{}/.kodiremote/kodiremote.ini'.format(getenv("HOME"))) #sending config file to config parser object
    displayPlaylist = config['settings']['playlist']
    kodi = Kodi()
    kodi.host = config['settings']['host'] 
    kodi.port = config['settings']['port']
    args = sys.argv[1:]
    if len(args) == 0:
        t = Terminal()
        with t.hidden_cursor(): 
            nowPlayingView(kodi)

    if len(args) >= 1:
        # Checks if an intersection of two lists yields any results.
        if bool(set(['h','H','help','--help','-help']) & set(args)):
            print("Run on its own or in one-shot mode with 'action' argument followed by any number of actions.")
            print("Useful ones include left,right,down,up,pause,skipnext,skipprevious.")
            print("You can find all valid input action arguments here:")
            print("http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action")
            print("valid arguments: [host $HOST] [port $PORT]")
            sys.exit(0)

        if 'host' in args:
            kodi.host = args[args.index('host') + 1]

        if 'port' in args:
            kodi.port = args[args.index('port') + 1]

        if args[0] == 'action':
            for i in args:
                print(kodi.inputAction(i))
            sys.exit(0)

        if 't' in args:
            sys.exit(0)

        t = Terminal()
        with t.hidden_cursor(): 
            nowPlayingView(kodi)

except (KeyboardInterrupt,OSError,ConnectionError):
    print(t.exit_fullscreen())
    print("Cannot connect to Kodi server. Is it running? Is your config file configured?")

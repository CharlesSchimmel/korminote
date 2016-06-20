#!/usr/bin/env python3

__name__="Charles Schimmelpfennig"
__license__="Creative Commons by-nc-sa"
__version__="0.7"
__status__="Development"

# imports
from blessed import Terminal
import sys
import configparser
from os import getenv
from time import  time
from kodiclient import KodiClient
import argparse

class Views:
    
    def __init__(self):
        kodi = KodiClient()
        term = Terminal()
        curProperties = ""
        windowID = 0
        playerid = 0

def keyParse(keyIn,windowID,kodi):
    """
    Brutish but python doesn't have switch/case and I'm not sure I want to use dictionaries for my functions.
    Also, can be somewhat optimized by putting most commmon commands at the beginning of the sequence.
    """

    if keyIn == 'q':
        print(t.exit_fullscreen())
        sys.exit(0)

    # Navigation and Actions
    elif keyIn == 'H' or keyIn.name == "KEY_DELETE":
        kodi.inputAction("back")
    elif keyIn == 'h' or keyIn.name == "KEY_LEFT":
        if windowID == 12005 or windowID == 12006:
            kodi.inputAction("stepback")
        kodi.inputAction("left")
    elif keyIn == 'l' or keyIn.name == "KEY_RIGHT":
        if windowID == 12005 or windowID == 12006:
            kodi.inputAction("stepforward")
        kodi.inputAction("right")
    elif keyIn == 'k' or keyIn.name == "KEY_UP":
        kodi.inputAction("up")
    elif keyIn == 'j' or keyIn.name == "KEY_DOWN":
        kodi.inputAction("down")
    elif keyIn.name == 'KEY_ENTER':
        if windowID != 10120:
            kodi.inputAction("select")
            kodi.inputAction("osd")
        else:
            kodi.inputAction("select")
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
    elif keyIn == '-':
        kodi.inputAction("volumedown")
    elif keyIn == '=':
        kodi.inputAction("volumeup")
    elif keyIn == '0':
        kodi.inputAction("mute")
    elif keyIn == 'c':
        kodi.inputAction("contextmenu")
    elif keyIn == 'i':
        kodi.inputAction("info")
    elif keyIn == 'u':
        kodi.updateAVLibrary("VideoLibrary")
    elif keyIn == 'U':
        kodi.updateAVLibrary("AudioLibrary")
    # Client-side commands
    elif keyIn.name == 'KEY_F1':
        helpView()
    elif keyIn.name == 'KEY_F2':
        recentEpsMenu(kodi,t)
    elif keyIn.name == 'KEY_F5':
        with t.location(y=6):
            print(t.clear())

def keyCap(kodi):
    """
    Main keycapture method. We have a short "repeat" window in the case the user wants to make many actions very quickly. Instead of capturing once per main loop, it contains a subloop that will listen for subsequent keypresses before returning to the main loop.
    This should help the latency as it no longer has to redraw the display.
    """
    prevTime = time()
    while True:
        windowID = kodi.getWindowID()
        with t.cbreak(): 
            keyIn = t.inkey(1)
            if keyIn != '':
                keyParse(keyIn,windowID,kodi)
                prevTime = time()
            elif keyIn == '':
                if time() - prevTime > 1:
                    break

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
    return usrIn

def nowPlayingView(kodi):
    # Upon activating any view, enter fullscreen and clear the old view.
    # This lets us restore previous views or terminal states
    print(t.enter_fullscreen(),t.clear())
    with t.location(y=0,x=0):
        print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))

    while True:
        # Move the cursor back to "rest." Not all terminals will hid ethe cursor like they sould. 
        print(t.move(0,0))

        playerid = kodi.getPlayerID() ### REQUEST
        windowID = kodi.getWindowID() ### REQUEST
        
        # Kodi gives a specific window id for the text entry prompt. If we get that, we know we can send text to it.
        if windowID == 10103:
            kodi.sendText(textPrompt(t))

        # Capture keys and send them to the parser.
        keyCap(kodi)

        # "Flush" the padding areas and title every few seconds.
        # No need to do it frequently. It disrupts the interface if done too often.
        # If the user resizes, stuff can get stuck in there as blessed doesn't redraw unless asked
        if int(time()) % 10 == 0:
            with t.location(y=0,x=0):
                print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))
            with t.location(y=1):
                print(t.center(""))
            with t.location(y=5):
                print(t.center(""))


        # If we get something for the playerid, something's playing.
        if playerid != -1:
            curProperties = kodi.playerProperties(playerid) ### REQUEST

            totalTime,curTime = kodi.getFormattedTimes(curProperties)

            times = "{}/{}".format(totalTime,curTime)
            title,artist = kodi.getTitle(playerid)
            title = str(title) # Every once in a while a False slips through. It'll only display for a second.

            progPerct = curProperties['result']['percentage']/100
            progWidth = t.width - len(times)
            progBar = int(progPerct*progWidth)

            if int(time()) % 5 == 0:
                if displayPlaylist.lower() == 'true':
                    playlistModule(kodi,t,title,curProperties)
            with t.location(y=2):
                if artist != '' and artist != False:
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
    try:
        playlist = kodi.getPlaylistItems(curProperties) ### REQUEST
        playlistItems = [ x['title'] for x in playlist ]
        if len(playlistItems) > 1:
            if playlistItems.index(title) > 2:
                # If we're a couple songs deep, We don't want to see the whole start of the playlist, just 2 before current
                playNum = playlistItems.index(title) - 2
                playlist = playlistItems[playNum:]


                for i in playlist[:t.height-7]:
                    with t.location(y=6+playlist.index(i)):
                        if i == title:
                            print(t.center(t.bold(t.white_on_black(i))))
                        else:
                            print(t.center(i))
            else:
                playlist = playlistItems

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
    with t.location(y=0):
        print(t.bold(t.blue("Controls:")))
        print("Largely similar to default Kodi controls \n")
        print("left,down,up,right : h,j,k,l")
        print("back : H")
        print("skip previous,next : [ ]")
        print("pause, stop : [space], x")
        print("volume down,up,mute : -,=,0")
        print("y : open youtube url")
        print("context menu : c")
        print("info : i")
        print("update video library : u")
        print("update video library : U")
        print("ESC/F11 : switch to/from media view")
        print("F1 : help")
        print("F2 : Recently added episodes")
        print("F5 : Refresh screen")
        print("q : quit")
    while True:
        with t.cbreak(): 
            keyIn = t.inkey(1)
            if keyIn == 'q' or keyIn.name == 'KEY_F1' or keyIn.name == "KEY_ENTER":
                print(t.exit_fullscreen(),t.clear())
                break

""" Set Constants """
config = configparser.ConfigParser() #initializing config parser object
config.read('{}/.korminote/config.ini'.format(getenv("HOME"))) #sending config file to config parser object
displayPlaylist = config['settings']['playlist']
kodi = KodiClient(config['settings']['host'],config['settings']['port'])

""" Parse arguments """
parser=argparse.ArgumentParser(description="Korminote: A terminal remote client for Kodi!")
parser.add_argument('-host', nargs='?', dest='host', help="Specify Kodi's host address.")
parser.add_argument('-port', nargs='?', dest='port', help="Specify Kodi's port address.")
parser.add_argument('-action', nargs='+', dest='action', help='Execute any number of valid Kodi actions. Pause, stop, next, etc. You can find more here: http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action')
parser.add_argument('-youtube', nargs='?', dest='youtube', help="Play a youtube url. Non-shortened only.")
parser.add_argument('-playing', action='store_true', dest='playing', help="Output currently playing title and (if available) artist in TITLE - ARTIST format.")
parser.add_argument('-t', action='store_true', dest='testing', help="Testing random functionalities.")

parg = parser.parse_args()

if parg.host:
    kodi.host = parg.host
if parg.port:
    kodi.port = parg.port
if parg.action:
    for i in parg.action:
        kodi.inputAction(i)
    sys.exit(0)
if parg.youtube:
    try:
        kodi.playYoutube(parg.youtube)
    except (OSError,ConnectionError):
        print("Can't connect to Kodi host. Is it running? Are host '{}' and port '{}' correct?".format(kodi.host,kodi.port))
if parg.playing:
    title,artist = kodi.getTitle()
    if artist != "" and artist != False:
        print("{} - {}".format(title,artist))
    elif title != "" and title != False:
        print(title)
    sys.exit(0)
if parg.testing:
    print('yay')
    sys.exit(0)

try:
    t = Terminal()
    with t.hidden_cursor(): 
        nowPlayingView(kodi)
except (OSError,ConnectionError):
    print(t.exit_fullscreen())
    print("Can't connect to Kodi host. Is it running? Are host '{}' and port '{}' correct?".format(kodi.host,kodi.port))
except KeyboardInterrupt:
    print(t.exit_fullscreen)

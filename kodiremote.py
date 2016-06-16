#!/usr/bin/env python3

# imports
from blessed import Terminal
import sys
import configparser
from os import getenv
from time import sleep, time
from KodiClient import Kodi

class Views:
    
    def __init__(self):
        kodi = Kodi()

def keyParse(keyIn,windowID,kodi):
    """
    Brutish but python doesn't have switch/case and I'm not sure I want to use dictionaries for my functions.
    Also, can be somewhat optimized by putting most commmon commands at the beginning of the sequence.
    """
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
        yturl = textPrompt(t,prompt="Enter Youtube Url")
        if yturl != "":
            try: 
                kodi.playYoutube(yturl)
            except:
                pass

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
    return usrIn


def nowPlayingView(kodi):
    # Upon activating any view, enter fullscreen and clear the old view.
    # This lets us restore previous views or terminal states
    print(t.enter_fullscreen(),t.clear())
    with t.location(y=0,x=0):
        print(t.center(t.cyan(t.bold("Kodi Terminal Remote"))))

    while True:
        # Move the cursor back to "rest." Shouldn't really be needed so long as
        # The terminal supports hidden cursor mode and the keycapture actually captures the keys
        # Neither of which are always true.
        print(t.move(0,0))

        playerid = kodi.getPlayerID()
        windowID = kodi.getWindowID()
        
        # Kodi gives a specific window id for the text entry prompt. If we get that, we know we can send text to it.
        if windowID == 10103:
            kodi.sendText(textPrompt(t))

        # Capture keys and send them to the parser.
        with t.cbreak(): 
            keyIn = t.inkey(1)
            keyParse(keyIn,windowID,kodi)

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
            print("Kodiremote: A terminal remote for Kodi.")
            print("Usage: ")
            print("\tkodiremote [host $HOST] [port $PORT] [action $ACTIONS] [youtube $URL]")
            print("\thost: specify Kodi host.")
            print("\tport: specify Kodi port. (8080 unless you specifically changed it.)")
            print("\taction: any number of valid actions. You can find all valid actions here: http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action")
            print("\tyoutube: a youtube url. Unshortened only.")
            sys.exit(0)

        if 'host' in args:
            try:
                kodi.host = args[args.index('host') + 1]
            except IndexError:
                print("Need a host.")

        if 'port' in args:
            try:
                kodi.port = args[args.index('port') + 1]
            except IndexError:
                print("Need a port.")

        if args[0] == 'action':
            for i in args:
                print(kodi.inputAction(i))
            sys.exit(0)

        if 'youtube' in args:
            # Hope to add to main application soon as well as reading from pipe
            # Only available as an argument for now.
            try:
                kodi.playYoutube(args[args.index('youtube')+1])
            except (IndexError):
                print("Need an url.")
            except (OSError,ConnectionError):
                print("Can't connect to Kodi host. Is it running? Are host '{}' and port '{}' correct?".format(kodi.host,kodi.port))
            sys.exit(0)

        if 'playing' in args:
            playerid = kodi.getPlayerID()
            if playerid != -1:
                title,artist = kodi.getTitle(playerid)
                if artist != "" and artist != False:
                    print("{} - {}".format(title,artist))
                else:
                    print(title)
            sys.exit(0)


        if 't' in args:
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

except (OSError,ConnectionError):
    print(t.exit_fullscreen())
    print("Cannot connect to Kodi server. Is it running? Is your config file configured?")
except KeyboardInterrupt:
    print(t.exit_fullscreen)

#!/usr/bin/env python3

__name__="Charles Schimmelpfennig"
__license__="Creative Commons by-nc-sa"
__version__="0.72"
__status__="Development"

# imports
from blessed import Terminal
import sys
import configparser
from os import getenv
from time import  time
from kodiclient import KodiClient
import argparse
from fuzzywuzzy import fuzz, process

class Views:

    def __init__(self,kodi):
        self.kodi = kodi
        self.term = Terminal()
        self.curProperties = ""
        self.windowID = 0
        self.playerid = 0

    def keyParse(self,keyIn):
        """
        Takes a key object from Terminal and parses it.
        Brutish but python doesn't have switch/case and I'm not sure I want to use dictionaries for my functions.
        Also, can be somewhat optimized by putting most commmon commands at the beginning of the sequence.
        """
        kodi = self.kodi
        t = self.term
        self.windowID = kodi.getWindowID()

        if keyIn == 'q':
            print(t.exit_fullscreen())
            sys.exit(0)

        # Navigation and Actions
        elif keyIn == 'H' or keyIn.name == "KEY_DELETE":
            kodi.inputAction("back")
        elif keyIn == 'h' or keyIn.name == "KEY_LEFT":
            if self.windowID == 12005 or self.windowID == 12006:
                kodi.inputAction("stepback")
            kodi.inputAction("left")
        elif keyIn == 'l' or keyIn.name == "KEY_RIGHT":
            if self.windowID == 12005 or self.windowID == 12006:
                kodi.inputAction("stepforward")
            kodi.inputAction("right")
        elif keyIn == 'k' or keyIn.name == "KEY_UP":
            kodi.inputAction("up")
        elif keyIn == 'j' or keyIn.name == "KEY_DOWN":
            kodi.inputAction("down")
        elif keyIn.name == 'KEY_ENTER':
            if self.windowID != 10120:
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
            with t.location(y=0):
                print(t.bold(t.center("Updating Video Library...")))
        elif keyIn == 'U':
            kodi.updateAVLibrary("AudioLibrary")
            with t.location(y=0):
                print(t.bold(t.center("Updating Audio Library...")))
        elif keyIn == 'm':
            self.playByArtist()


        # Client-side commands
        elif keyIn.name == 'KEY_F1':
            self.helpView()
        elif keyIn.name == 'KEY_F2':
            self.recentEpsMenu()
        elif keyIn.name == 'KEY_F5':
            with t.location(y=6):
                print(t.clear())

    def keyCap(self):
        """
        Main keycapture method. We have a short "repeat" window in the case the user wants to make many actions very quickly. Instead of capturing once per main loop, it contains a subloop that will listen for subsequent keypresses before returning to the main loop.
        This should help the latency as it no longer has to redraw the display.
        """
        t = self.term
        prevTime = time()
        while True:
            with t.cbreak():
                keyIn = t.inkey(1)
                if keyIn != '':
                    self.keyParse(keyIn)
                    prevTime = time()
                elif keyIn == '':
                    if time() - prevTime > 1:
                        break

    def recentEpsMenu(self):
        """
        Displays a menu of the 25 recently added episodes. Sends selection to kodi.open. If no new episodes, displays that.
        """
        kodi = self.kodi
        t = self.term
        recentEpsList = kodi.getRecentEps()
        if recentEpsList != False:
            selectionLabel,selectionIndex = self.menuView([ x['label'] for x in recentEpsList],"Recent Episodes:")
            if selectionLabel != False:
                kodi.openFile(recentEpsList[selectionIndex]['file'])
        else:
            with t.location(y=0):
                print(t.bold(t.center("No Recent Episodes")))

    def textPrompt(self,prompt="Enter Text: ",ylocation=5):
        """
        Displays a text prompt and returns whatevever the user entered.
        """
        t = self.term
        with t.location(x=0,y=ylocation):
            print(t.bold_blue("▒"*(t.width//2)))
        with t.location(x=0,y=ylocation):
            usrIn = input(t.bold_blue(prompt))
        with t.location(x=0,y=ylocation):
            print(" "*t.width)
        return usrIn

    def header(self):
        t = self.term
        with t.location(y=0):
            print(t.bold(t.bright_red("Korminote")),t.bright_blue_on_white("F1 Help"),t.bright_blue_on_white("F2 Recent Episodes"),t.bright_blue_on_white("F5 Refresh"))

    def playByArtist(self):
        usrArtist = self.textPrompt("Artist: ")
        artistDict = {}
        for x in kodi.getArtists():
            artistDict[x['artist']] = x['artistid']
        match = process.extractOne(usrArtist,artistDict.keys())[0]
        artistID = artistDict[match]
        albumDict = {}
        for x in kodi.getAlbums():
            albumDict[x['title']] = x['artistid']
        print(albumDict[artistDict[match]])

    def nowPlayingView(self):
        """
        Essentially the main loop. Does all the handling for displaying information to the user.
        """
        kodi = self.kodi
        t = self.term

        # Upon activating any view, enter fullscreen and clear the old view.
        # This lets us restore previous views or terminal states
        print(t.enter_fullscreen(),t.clear())
        self.header()

        while True:

            # Move the cursor back to "rest." Not all terminals will hid ethe cursor like they sould.
            print(t.move(0,0))

            self.playerid = kodi.getPlayerID() ### REQUEST
            self.windowID = kodi.getWindowID() ### REQUEST

            # Kodi gives a specific window id for the text entry prompt. If we get that, we know we can send text to it.
            if self.windowID == 10103:
                kodi.sendText(self.textPrompt())

            self.keyCap()

            # "Flush" the padding areas and title every few seconds. It disrupts the interface if done too often.
            if int(time()) % 5 == 0:
                self.header()
                with t.location(y=1):
                    print(t.center(""))
                with t.location(y=5):
                    print(t.center(""))


            # If we get something for the playerid, something's playing.
            if self.playerid != -1:
                tempProperties = kodi.playerProperties(self.playerid) ### REQUEST
                try:
                    testValue = tempProperties['result']
                    self.curProperties = tempProperties
                except: pass
                totalTime,curTime = kodi.getFormattedTimes(self.curProperties)

                times = "{}/{}".format(totalTime,curTime)
                title,artist = kodi.getTitle(self.playerid)
                if title == False: title = "" # Every once in a while a False slips through. It'll only display for a second.
                if len(title) > t.width:
                    title = title[:t.width-5]+"..."

                try:
                    progPerct = self.curProperties['result']['percentage']/100
                except: pass
                progWidth = t.width - len(times)
                progBar = int(progPerct*progWidth)

                if int(time()) % 5 == 0:
                    if displayPlaylist.lower() == 'true':
                        self.playlistModule(title)
                with t.location(y=2):
                    if artist != '' and artist != False:
                        print(t.center(t.bold(title) +" - {}".format(artist)))
                    else:
                        print(t.center(t.bold(title)))

                if self.curProperties['result']['speed'] == 0:
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

    def playlistModule(self,title):
        try:
            playlist = kodi.getPlaylistItems(self.curProperties) ### REQUEST
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
        except: pass

    def menuView(self,options,title=False):
        term = self.term
        offset=2 # Spacing for instructions/title
        print(term.enter_fullscreen(),term.move(offset-1,0))
        while True:
            if title:
                with term.location(y=0):
                    print(t.center(t.bold(t.bright_red(title))))
            with term.location(y=1):
                print(term.bold(term.blue(term.center("Enter to select, q to cancel."))))

            cursy,cursx = term.get_location()
            if cursy not in range(offset,term.height):
                term.move(offset,cursx)

            for i in range(0,len(options[:term.height - offset-1])): # Only show as many as can fit on the screen + spacing
                # Need to compensate for the way the cursor is show on the screen. Hence -1 -offset
                if cursy-1-offset == i:
                    with term.location(y=i+offset):
                        print(term.center(term.green_on_black(term.bold(options[i]))))
                else:
                    with term.location(y=i+offset):
                        print(term.center(options[i]))

            with term.cbreak():
                key = term.inkey(1)
                if key == "q" or key.name == "KEY_F2":
                    print(term.exit_fullscreen())
                    return False,False
                elif key.name == "KEY_UP" or key == 'k':
                    if cursy-1 > offset:
                        print(term.move_up(),end="")
                elif key.name == "KEY_DOWN" or key == 'j':
                    if cursy+1 < t.height and cursy < len(options)+offset:
                        print(term.move_down(),end="")
                elif key.name == "KEY_ENTER" or key == ' ':
                    print(term.exit_fullscreen())
                    return options[cursy-1-offset],cursy-1-offset

    def helpView(self):
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

parser.add_argument('-notif', nargs=3, dest='notif', help="Send a notification. -notification TITLE MESSAGE DISPLAYTIME(in milliseconds)")

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
    try:
        title,artist = kodi.getTitle()
        if artist != "" and artist != False:
            print("{} - {}".format(title,artist))
        elif title != "" and title != False:
            print(title)
    except: pass
    sys.exit(0)

if parg.notif:
    try:
        kodi.sendNotification(parg.notif[0],parg.notif[1],parg.notif[2])
        sys.exit(0)
    except:
        sys.exit(0)

if parg.testing:
    print(kodi.sendNotification(title="Yay!", message="Yaaaaay"))
    sys.exit(0)


try:
    t = Terminal()
    with t.hidden_cursor():
        view = Views(kodi)
        view.nowPlayingView()
except (OSError,ConnectionError):
    print(t.exit_fullscreen())
    print("Can't connect to Kodi host. Is it running? Are host '{}' and port '{}' correct?".format(kodi.host,kodi.port))
except KeyboardInterrupt:
    print(t.exit_fullscreen)

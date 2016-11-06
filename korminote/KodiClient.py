#!/usr/bin/env python3
__name__="KodiClient"
__license__="Creative Commons by-nc-sa"
__version__="0.73"
__status__="Development"

import requests
import re
import json

class KodiClient:
    """
    Contains methods relating to interacting with a Kodi instance's JSON server.
    """


    def __init__(self,kodiHost="localhost",kodiPort=8080):
        self.host = kodiHost
        self.port = kodiPort
        self.headers = {'Content-Type': 'application/json'}
        self.curPlayerProperties = {}

    def template_request(self,method,params={}):
        payload = {"id":"1","jsonrpc":"2.0","method":method,"params":params}
        payload = json.JSONEncoder().encode(payload)
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return r.json()

    def inputAction(self,action):
        """
        Sends the given action specified by: http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action
        Left, Right, Up, Down, Back, Pause, etc.
        Returns the server's JSON response.
        """
        method = "Input.ExecuteAction"
        params = {"action":"{}".format(action)}
        return self.template_request(method,params)

    def updateAVLibrary(self,library):
        """
        Given the specified library type (VideoLibrary or AudioLibrary), asks the kodi server to update it.
        Returns the server's JSON response.
        """
        method = "{}.Scan".format(library)
        return self.template_request(method)

    def cleanAVLibrary(self,library):
        """
        Given the specified library type (VideoLibrary or AudioLibrary), asks the kodi server to clean it.
        Returns the server's JSON response.
        """
        method = "{}.Clean".format(library)
        return self.template_request(method)

    def sendText(self,text):
        """
        Takes a given string and sends it as input.
        Returns the server's JSON response.
        """
        method = "Input.SendText"
        params = {"text":"{}".format(text)}
        return self.template_request(method,params)

    def getWindowID(self):
        """
        Queries the server and returns the currently active window number.
        """
        method = "GUI.GetProperties"
        params = {"properties":["currentwindow"]}
        return self.template_request(method,params)['result']['currentwindow']['id']

    def updateCurPlayerProperties(self,playerid=-1):
        """
        Currently not useful. I think it is better to store the properties outside the object. Not sure.
        That way, the user can decide whether to specify them everytime if they would like rather than expect them to update the local object.
        """
        if playerid == -1:
            self.curPlayerProperties = self.playerProperties()
        else:
            self.curPlayerProperties = self.playerProperties(playerid=playerid)

    def playerProperties(self,playerid=-1):
        """
        Queries the server and returns the currently active players properties.
        """
        if playerid == -1:
            playerid = self.getPlayerID()

        method = "Player.GetProperties"
        params = {"playerid":playerid,"properties":["playlistid","time","totaltime","percentage","type","speed"]}
        return self.template_request(method,params)

    def getPlayerID(self):
        """
        Queries the server and returns the player id as a string (0-2).
        If there's none to be found (ie nothing is playing) returns -1.
        """
        method = "Player.GetActivePlayers"
        try:
            return self.template_request(method)['result'][0]['playerid']
        except (IndexError):
            return -1 # The player ID can be 0 so we can't use False

    def getTitle(self,playerid=-1):
        """
        Ideally returns the title,artist(or showtitle) of the currently playing media.
        Returns False,False if such information isn't available (ex: pictures, obscure plugins.)
        Will get playerid itself if not defined. Recommended to define playerid to limit number of requests.
        """
        if playerid == -1:
            playerid = self.getPlayerID()
        try:
            method = "Player.GetItem"
            params = {"playerid":playerid,"properties":["title","artist","showtitle"]}
            result = self.template_request(method,params)
            title = result['result']['item']['title']
            if 'showtitle' not in result['result']['item']:
                artist = result['result']['item']['artist'][0]
            else:
                artist = result['result']['item']['showtitle']
            return title,artist
        except:
            return False,False

    def getFormattedTimes(self,curProperties=False):
        """
        Either takes already available current properties or queries for them and formats the total and current time.
        Returns two strings (current and remaining) in either h:mm:ss (if hour > 0) or mm:ss format.
        Preferred to make one Player.Properties call and use it for multiple functions to save on queries.
        """
        if not curProperties:
            curProperties = self.playerProperties()
        try:
            if curProperties['result']['totaltime']['hours'] == 0:
                curTime =  "{}:{:02d}".format(curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
                totalTime = "{}:{:02d}".format(curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
            else:
                curTime =  "{}:{:02d}:{:02d}".format(curProperties['result']['time']['hours'],curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
                totalTime = "{}:{:02d}:{:02d}".format(curProperties['result']['totaltime']['hours'],curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
        except:
            return "00:00","00:00"
        return curTime,totalTime

    def getRecentEps(self):
        """
        Queries the server for recently added episodes.
        Returns a list (sorted, recently added first) of dictionaries for each episode.
        Dictionaries contain keys: episodeid, label, episode title, file, showtitle
        Returns false if no episodes are found.
        """
        method = "VideoLibrary.GetRecentlyAddedEpisodes"
        params = {"properties":["title","showtitle","file"]}
        result = self.template_request(method,params)
        try:
            return result['result']['episodes']
        except (IndexError,KeyError):
            return False

    def getArtists(self):
        """
        """
        method = "AudioLibrary.GetArtists"
        try:
            return self.template_request(method)['result']['artists']
        except (IndexError,KeyError):
            return False

    def getAlbums(self):
        """
        """
        method = "AudioLibrary.GetAlbums"
        params = {"properties":["artistid","title","artist"]}
        try:
            return self.template_request(method,params)['result']['albums']
        except (IndexError,KeyError):
            return False

    def sendNotification(self,title='',message='',displaytime=5000):
        """
        """
        method = "GUI.ShowNotification"
        params = {"title":title,"message":message,"displaytime":displaytime}
        return self.template_request(method,params)

    def playYoutube(self,yturl):
        """
        Regexes a youtube url and grabs just the video id. Sends it to the youtube plugin.
        """
        pattern =  (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        ytregex = re.match(pattern, yturl)
        if ytregex:
            yturl = ytregex.group(6)
            self.openFile("plugin://plugin.video.youtube/?action=play_video&videoid={}".format(yturl))
        else:
            self.sendNotification(title='Invalid Youtube URL')

    def getPlaylistItems(self,curProperties=False):
        """
        Returns a list (of dicts) of items in the playlist. Doesn't need to be given the current properties (which contains the playlistid for the current playlist.)
        """

        if not curProperties:
            playlistid = self.playerProperties()['result']['playlistid']
        else:
            playlistid = curProperties['result']['playlistid']
        try:
            method = "Playlist.GetItems"
            params = {"playlistid":playlistid,"properties":["title"]}
            return self.template_request(method,params)['result']['items']
        except:
            return False

    def getEpDetails(self,episodeid):
        """
        When given the unique ID of an episode in the library, it returns information about that episode.
        """
        method = "VideoLibrary.GetEpisodeDetails"
        params = {"episodeid":episodeid,"properties":["file"]}
        return self.template_request(method,params)['result']['episodedetails']

    def openFile(self,targetFile):
        """
        Opens a file for playback given a path. This path can also be one of the plugin paths like plugin://plugin.video.youtube etc
        Returns the server's JSON response.
        """
        method = "Player.Open"
        params = {"item":{"file":targetFile}}
        return self.template_request(method,params)

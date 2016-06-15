#!/usr/bin/env python3
import requests

class Kodi:
    """
    Contains methods relating to interacting with a Kodi instance's JSON server.
    Note: Kodi doesn't respond with typical HTTP error codes.
    """

    def __init__(self):
        self.host = "localhost"
        self.port = 8080
        self.headers = {'Content-Type': 'application/json'}

    def inputAction(self,action):
        """
        Sends the given action specified by: http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action
        Left, Right, Up, Down, Back, Pause, etc.
        Returns the server's JSON response.
        """
        payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.ExecuteAction","params":{"action":"'+action+'"}}'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return r.json()

    def updateAVLibrary(self,library):
        """
        Given the specified library type (VideoLibrary or AudioLibrary), asks the kodi server to update it.
        Returns the server's JSON response.
        """
        payload = '{"id": "1", "jsonrpc": "2.0", "method": "'+library+'.Scan"}}'
        r = requests.post("http://{}:{}/jsonrpc".format(kodiHost,kodiPort), data=payload, headers=self.headers)
        return r.json()

    def sendText(self,text):
        """
        Takes a given string and sends it as input.
        Returns the server's JSON response.
        """
        payload = '{"id": "1", "jsonrpc": "2.0", "method": "Input.SendText","params":{"text":"'+text+'"}}'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return(r.json())

    def getWindowID(self):
        """
        Queries the server and returns the currently active window number.
        """
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "GUI.GetProperties", "params":{"properties":["currentwindow"]} }'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return r.json()['result']['currentwindow']['id']

    def playerProperties(self,playerid=False):
        """
        Queries the server and returns the currently active players properties.
        """
        if playerid == False:
            playerid = self.getPlayerID()
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetProperties", "params":{"playerid":'+playerid+',"properties":["playlistid","time","totaltime","percentage","type","speed"]} }'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return r.json()

    def getPlayerID(self):
        """
        Queries the server and returns the player id as an integer.
        If there's none to be found (ie nothing is playing) returns false.
        """
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetActivePlayers" }'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        try:
            return str(r.json()['result'][0]['playerid'])
        except (IndexError):
            return False

    def getTitle(self,playerid=False):
        """
        Ideally returns the title,artist(or showtitle) of the currently playing media.
        Returns False,False if such information isn't available (ex: pictures, obscure plugins.)
        Will get playerid itself if not defined. Recommended to define playerid to limit number of requests.
        """
        if playerid == False:
            playerid = self.getPlayerID()
        try:
            payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.GetItem", "params":{"playerid":'+playerid+',"properties":["title","artist","showtitle"]} }'
            r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
            title = r.json()['result']['item']['title']
            if 'showtitle' not in r.json()['result']['item']:
                artist = r.json()['result']['item']['artist'][0]
            else:
                artist = r.json()['result']['item']['showtitle']
            return title,artist
        except:
            return False,False

    def getFormattedTimes(self,curProperties=False):
        """
        Either takes already available current properties or queries for them and formats the total and current time.
        Returns two strings (current and remaining) in either h:mm:ss (if hour > 0) or mm:ss format.
        Preferred to make one Player.Properties call and use it for multiple functions to save on queries.
        """
        if curProperties == False:
            curProperties = self.playerProperties()
        try:
            if curProperties['result']['totaltime']['hours'] == 0:
                curTime =  "{}:{:02d}".format(curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
                totalTime = "{}:{:02d}".format(curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
            else:
                curTime =  "{}:{:02d}:{:02d}".format(curProperties['result']['time']['hours'],curProperties['result']['time']['minutes'],curProperties['result']['time']['seconds'])
                totalTime = "{}:{:02d}:{:02d}".format(curProperties['result']['totaltime']['hours'],curProperties['result']['totaltime']['minutes'],curProperties['result']['totaltime']['seconds'])
        except:
            return "00:00/00:00"
        return curTime,totalTime

    def getRecentEps(self):
        """
        Queries the server for recently added episodes.
        Returns a list (sorted, recently added first) of dictionaries for each episode.
        Dictionaries contain keys: episodeid, label, episode title, file, showtitle
        Returns false if no episodes are found.
        """
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "VideoLibrary.GetRecentlyAddedEpisodes", "params":{"properties":["title","showtitle","file"]}} '
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        try:
            return r.json()['result']['episodes']
        except (IndexError,KeyError):
            return False

    def getPlaylistItems(self,curProperties=False):
        if curProperties == False:
            playlistid = str(self.playerProperties()['result']['playlistid'])
        else:
            playlistid = str(curProperties['result']['playlistid'])
        try:
            payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Playlist.GetItems", "params":{"playlistid":'+playlistid+',"properties":["title"]} }'
            r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
            return r.json()['result']['items']
        except:
            return False

    def getEpDetails(self,episodeid):
        episodeid = str(episodeid)
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params":{"episodeid":'+episodeid+',"properties":["file"]} }'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return r.json()['result']['episodedetails']

    def openFile(self,targetFile):
        payload = '{ "id": "1", "jsonrpc": "2.0", "method": "Player.Open", "params":{"item":{"file":"'+targetFile+'"}}}'
        r = requests.post("http://{}:{}/jsonrpc".format(self.host,self.port), data=payload, headers=self.headers)
        return r.json()

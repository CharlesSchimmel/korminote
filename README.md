# KodiRemote

Kodiremote: A terminal remote for Kodi.

Usage:

    kodiremote [host $HOST] [port $PORT] [action $ACTIONS] [youtube $URL]
    host: specify Kodi host.
    port: specify Kodi port. (8080 unless you specifically changed it.)
    action: runs any number of valid actions then exits. You can find all valid actions here: http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action
    youtube: opens a youtube url and exits. Unshortened only.
    playing: prints '$title - $artist' or just 'title' if no artist available.

Configure with $HOME/.kodiremote/kodiremote.ini

![Screenshot](kodiremote.jpg?raw=true)

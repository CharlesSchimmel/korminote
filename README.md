# Korminote

## Version: 0.7

Korminote: A terminal remote for Kodi!

Install with "install.sh" or "python3 setup.py install" or on Arch Linux: "makepkg -s". Uninstall with "install.sh uninstall".

Usage:

    korminote -host [$HOST] -port [$PORT] -action [$ACTIONS] -youtube [$URL] -playing
    host: specify Kodi host.
    port: specify Kodi port. (8080 unless you specifically changed it.)
    action: runs any number of valid actions then exits. You can find all valid actions here: http://kodi.wiki/view/JSON-RPC_API/v6#Input.Action
    youtube: opens a youtube url and exits. Unshortened only.
    playing: prints '$title - $artist' or just 'title' if no artist available. Returns nothing if nothing available.

Configure with $HOME/.korminote/config.ini

![Screenshot](scrot.jpg?raw=true)

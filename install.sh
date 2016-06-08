#!/bin/bash
APP=$HOME/.kodiremote/
CONFIG="$APP"kodiremote.ini
BINLOC=/usr/local/bin/kodiremote

if [ "$(id -u)" == "0" ]; then
	echo "Don't use sudo for this script or it'll install into root's HOME"
	exit 1
else
    echo "This will install 'kodiremote'"
    echo "Checking dependencies:"

    #Check if python3 installed
    python3 --version >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Python3 is not installed. Please install python3 and install again."
    else
        echo -n "Python3 found..."
    fi

    # Check if pip3 is installed
    pip3 --version >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then # Either pip3 isn't installed or requests isn't installed.
        echo "Pip3 not installed. If you believe you have the Blessed package installed, you may continue."
        echo -n "Continue? [y/N]"
        read usrIn
        if [[ usrIn -eq '' ]] || [[ usrIn -eq 'n' ]] || [[ usrIn -eq 'N' ]]; then
            exit 1
        fi
    else
        echo -n "pip3 found..."
    fi

    pip3 show blessed >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then # Either pip3 isn't installed or requests isn't installed.
        echo "Blessed is not installed. May I install it for you? [Y/n]"
        read usrIn
        if [[ usrIn -eq '' ]] || [[ usrIn -eq 'y' ]] || [[ usrIn -eq 'Y' ]]; then
            sudo pip3 install blessed
        else
            exit 1
        fi
    else
        echo -n "blessed found..."
    fi

    #check if app location exists; only make it if it exists
    if ! [[ -e $APP ]]; then
        mkdir -m 777 $APP
    fi

    #cp will overwrite
    cp -p kodiremote.py $APP

    echo "Making symlink to /usr/local/bin/kodiremote"
    sudo rm $BINLOC
    sudo ln -s "$APP"kodiremote.py $BINLOC


    if ! [[ -e $CONFIG ]]; then
        echo "Copying config..."
        cp -p kodiremote.ini $CONFIG
    else
        cp -p kodiremote.ini $CONFIG.default
    fi

    echo "Done."
    echo "Please edit the config file at $CONFIG and run 'kodiremote' to run."
fi

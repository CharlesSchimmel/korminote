#!/bin/bash
APP=$HOME/.korminote/
CONFIG="$APP"config.ini
SYMLOC=/usr/bin/korminote
OPT=/opt/korminote/

install () {
    echo "This will install Korminote! A Kodi Remote for the terminal!"
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
        echo "Pip3 not installed. If you believe you have the Blessed package for python3 installed, you may continue. The program will not function without."
        echo -n "Continue? [y/N]"
        read usrIn
        if [[ usrIn -eq '' ]] || [[ usrIn -eq 'n' ]] || [[ usrIn -eq 'N' ]]; then
            exit 1
        fi
    else
        echo -n "pip3 found..."
        pip3 show blessed >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then # Pip3 returns 0 if show works; blessed installed
            echo "Blessed is not installed or I otherwise cannot find it. May I install it for you? [Y/n]"
            read usrIn
            if [[ usrIn -eq '' ]] || [[ usrIn -eq 'y' ]] || [[ usrIn -eq 'Y' ]]; then
                sudo pip3 install blessed
            else:
                echo "Blessed for python3 is required for this program. If you believe it is installed outside of pip3, you may continue."
                read usrIn
            fi
        else
            echo -n "blessed found..."
        fi
    fi

    #check if app location exists; only make it if it exists
    if ! [[ -e $APP ]]; then
        mkdir -m 777 $APP
    fi
    if ! [[ -e $OPT ]]; then
        sudo mkdir $OPT
    fi

    #cp will overwrite
    sudo cp -p korminote.py $OPT
    sudo cp -p kodiclient.py $OPT

    echo -n "Making symlink to /usr/bin/korminote..."
    sudo rm $SYMLOC
    sudo ln -s "$OPT"korminote.py $SYMLOC


    if ! [[ -e $CONFIG ]]; then
        echo "Copying config..."
        cp -p config.ini $CONFIG
    else
        cp -p config.ini $CONFIG.default
    fi

    echo "Done."
    echo "Please edit the config file at $CONFIG and run 'korminote' to run."
}

uninstall () {
    echo "This will uninstall KoRmiNote... :("
    echo "Deleting opt folder $OPT"
    sudo rm -r "$OPT"
    echo  "Deleting config folder $APP"
    sudo rm -r "$APP"
    echo  "Deleting symlink $SYMLOC"
    sudo rm $SYMLOC
    echo "All done. Feedback is appreciated!"
    echo "https://github.com/charlesschimmel/korminote"
}


if [ "$(id -u)" == "0" ]; then
	echo "Don't use sudo for this script or it'll install into root's HOME"
	exit 1
else
    if [[ $1 == "uninstall" ]] || [[ $1 == "u" ]]; then
        uninstall
    else
        install
    fi
fi


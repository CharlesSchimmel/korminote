#!/bin/bash
APP=$HOME/.korminote/
CONFIG="$APP"config.ini

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
        pip3 show setuptools >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then # Pip3 exits 0 if show works; blessed installed
            echo "Setuptools is not installed. Attempting to install..."
                sudo pip3 install setuptools
        else
            echo -n "setuptools found..."
        fi
    fi

    sudo python3 setup.py install
    if ! [[ -e $CONFIG ]]; then
        if ! [[ -e $APP ]]; then
            mkdir $APP
        fi
        echo "Copying config..."
        cp -p ./config.ini $CONFIG
    else
        cp -p ./config.ini $CONFIG.default
    fi

    echo "Done."
    echo "Please edit the config file at $CONFIG and run 'korminote' to run."
}

uninstall () {
    echo "This will uninstall KoRmiNote... :("
    sudo pip3 uninstall korminote 
    echo "All done. Feedback is appreciated!"
    echo "https://github.com/charlesschimmel/korminote"
}

update () {
    tmpdir=$(echo $RANDOM)
    git clone https://github.com/charlesschimmel/korminote /tmp/$tmpdir
    exec /tmp/$tmpdir/install.sh
    rm -r /tmp/$tmpdir
}

if [[ $1 == "uninstall" ]]; then
    uninstall
elif [[ $1 == "update" ]]; then
    update
else
    if [ "$(id -u)" == "0" ]; then
            echo "Don't use sudo for this script or it'll install into root's HOME"
            exit 1
    else
        install
    fi
fi


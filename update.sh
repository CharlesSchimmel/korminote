#!/bin/bash
gitVersion=`curl -s https://raw.githubusercontent.com/CharlesSchimmel/korminote/master/README.md | grep -i version | sed -r 's/^.+?: //g'| sed 's/ //g'`
yourVersion=`cat /opt/korminote/korminote.py | grep version | sed -r 's/(^.+?=|")//g' | sed 's/ //g'`

tmpdir=$(echo $RANDOM)
bcval=$(bc <<< "$yourVersion < $gitVersion")
if [[ $bcval -eq 1 ]]; then
    echo "An update is available. Would you like to download and install it? [Y/n]"
    read usrIn
    if [[ $usrIn == '' ]] || [[ $usrIn == 'Y' ]] || [[ $usrIn == 'y' ]] ; then
        git clone https://github.com/charlesschimmel/korminote /tmp/$tmpdir
        exec /tmp/$tmpdir/install.sh
        rm -r /tmp/$tmpdir
    else
        exit 0
    fi
else
    echo "You are up to date!"
fi



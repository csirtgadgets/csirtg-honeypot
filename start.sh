#!/bin/sh

set -e

cd $(dirname $0)

if [ "$1" != "" ]
then
    VENV="$1"

    if [ ! -d "$VENV" ]
    then
        echo "The specified virtualenv \"$VENV\" was not found!"
        exit 1
    fi

    if [ ! -f "$VENV/bin/activate" ]
    then
        echo "The specified virtualenv \"$VENV\" was not found!"
        exit 2
    fi

    echo "Activating virtualenv \"$VENV\""
    . $VENV/bin/activate
fi

twistd --version

echo "Starting wf-rdp in the background..."
twistd -y rdp.tac -l rdp.log --pidfile rdp.pid

echo "Starting wf-vnc in the background..."
twistd -y vnc.tac -l vnc.log --pidfile vnc.pid

#echo "Starting wf-http in the background..."
#twistd -y http.tac -l http.log --pidfile http.pid

#!/bin/sh

PIDFILE="vnc.pid rdp.pid"

cd $(dirname $0)

for P in $PIDFILE; do
    PID=$(cat $P 2>/dev/null)

    if [ -n "$PID" ]; then
        echo "Stopping $PID...\n"
        kill -TERM $PID
    fi
done

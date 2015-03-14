#!/bin/sh

PIDFILE=rdp.pid

cd $(dirname $0)

PID=$(cat $PIDFILE 2>/dev/null)

if [ -n "$PID" ]; then
  echo "Stopping wf-rdp...\n"
  kill -TERM $PID
fi
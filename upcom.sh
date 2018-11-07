#!/bin/bash

DEFAULT_WORKDIR="./esp8266"
DEFAULT_AMPY_BAUD=115200
DEFAULT_AIO_EXIT=0.01

AIO_EXIT=${AIO_EXIT:-$DEFAULT_AIO_EXIT}

clear

export WORKDIR=${WORKDIR:-$DEFAULT_WORKDIR}
export AMPY_PORT=${1:-/dev/ttyUSB0}
export AMPY_BAUD=${AMPY_BAUD:-115200}


if [[ $# -lt 1 ]]; then
    echo
    echo "Usage:"
    echo
    echo "  AMPY_BAUD=${AMPY_BAUD} WORKDIR=somedir $0 serial-port [ <stty-options> ... ] ]"
    echo
    echo "  Example: WORKDIR=${WORKDIR} $0 ${AMPY_PORT}"
    echo
    echo "  Press Ctrl+Q to quit $0 any time"
    exit
fi

#LTP=$(python3.7 -u -B -c "import time;tm=time.gmtime();tm = tm[0:3] + (0,) + tm[3:6] + (0,);print(tm)")
# pausing asyncio loop on the board to get exclusive repl
#cat >> $1 <<END
#use.aio.__class__.paused=True;__import__('machine').RTC().datetime(${LTP})
#END

# adjust if you have a long exit loop
#sleep $AIO_EXIT

PYTHONPATH=$(dirname "$(realpath $0)"):$PYTHONPATH python3.7 -u -B -mstupyde.upcom


# Exit when any command fails
set -e

# Save settings of current terminal to restore later
original_settings="$(stty -g)"

# Kill background process and restore terminal when this shell exits
trap 'set +e; kill "$bgPid"; stty "$original_settings"' EXIT

# Remove serial port from parameter list, so only stty settings remain
port="$1"; shift

# Set up serial port, append all remaining parameters from command line
#stty -F "$port" raw -echo "$@"
stty -F "$port" raw -echo $AMPY_BAUD "$@"

# Set current terminal to pass through everything except Ctrl+Q
# * "quit undef susp undef" will disable Ctrl+\ and Ctrl+Z handling
# * "isig intr ^Q" will make Ctrl+Q send SIGINT to this script
stty raw -echo isig intr ^Q quit undef susp undef

# Let cat read the serial port to the screen in the background
# Capture PID of background process so it is possible to terminate it
cat "$port" & bgPid=$!

# Redirect all keyboard input to serial port
cat >"$port"

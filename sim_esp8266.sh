#!/bin/bash
STUD=$(dirname "$(realpath $0)")

DEFAULT_WORKDIR="./esp8266"
DEFAULT_UPY="./1.9.5/micropython/ports/unix/micropython"
DEFAULT_MPY="./1.9.5/micropython/mpy-cross/mpy-cross"
DEFAULT_UHOME="./1.9.5/home"

export WORKDIR=${WORKDIR:-$DEFAULT_WORKDIR}
export UPY=$(realpath ${UPY:-$DEFAULT_UPY})
export MPY=$(realpath ${MPY:-$DEFAULT_MPY})

UHOME=$(realpath ${UHOME:-$DEFAULT_UHOME})

cd ${WORKDIR}

export MICROPYPATH=.:./assets:$UHOME:$UHOME/site-packages:$UHOME/lib-dynload:$STUD

echo Running simulation from : $(pwd)
echo Interpreter : ${UPY}
echo Compiler : ${MPY}

( sleep 3 && pidof micropython >>/tmp/log) &
clear > /tmp/log
${UPY} -X heapsize=107000 -i $STUD/sim_esp8266.py "$@" 2>>/tmp/log
python3.7 -u -B <<END
import sys;
sys.stdout.write( chr(0x1b)+"[?1003l")
sys.stdout.flush()
END
stty sane

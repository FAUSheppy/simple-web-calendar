#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Ussage: ./deploy.sh [ICS-FILE] [DEPLOY-TARGET]"
    exit 1
fi

ICS=${1}
DEPLOY=${2}

while /bin/true
do
    echo -n "Reubuild at: "
    date
    ./python/cal.py $ICS $DEPLOY css js
    inotifywait -e modify $ICS
done
chmod -R a+rX $DEPLOY

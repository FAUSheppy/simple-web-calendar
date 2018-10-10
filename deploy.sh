#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Ussage: ./deploy.sh [ICS-FILE] [DEPLOY-TARGET]"
    exit 1
fi

ICS=${1}
DEPLOY=${2}

# copy css/js
cp -f -r css/ ${DEPLOY}/css
cp -f -r js/ ${DEPLOY}/js

# fix permissions to be sure
chown -R :www-data $DEPLOY
chmod -R g+rX $DEPLOY

while /bin/true
do

    # output date for debug
    echo -n "Reubuild at: "
    date

    # run the build
    ./python/cal.py $ICS $DEPLOY css js


    # wait for changes
    inotifywait -e modify -r $ICS

done

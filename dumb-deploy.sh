#!/bin/bash
ICS=$1
DEPLOY=$2

# copy css/js
cp -f -r css/ ${DEPLOY}/
cp -f -r js/ ${DEPLOY}/

# run the build
./python/cal.py $ICS $DEPLOY css js

# mandatory timeut
sleep 1
    
# fix permissions to be sure
chown -R :www-data $DEPLOY
chmod -R g+rX $DEPLOY

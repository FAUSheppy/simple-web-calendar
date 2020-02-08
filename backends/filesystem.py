#!/usr/bin/python3
import os
import re
import uuid

import pytz
import locale
import flask

import icalendar
import calendar
from datetime import datetime

import utils.timeframe as timeframe
import utils

import requests

forceReload = False

def _parse(path):

    # get all files to be read #
    srcDir = ""
    if os.path.isdir(path):
        srcDir = path
        files = os.listdir(path)
    else:
        files = [path]

    # get events from files #
    events = []
    for fname in files:
        if not fname.endswith(".ics"):
            continue
        with open(os.path.join(srcDir, fname), 'rb') as f:
            events += utils.parsing.parseEventData(f.read())

    return sorted(events, key=lambda x: utils.parsing.localizeDatetime(x.get('dtstart').dt))

def getEvents(start, end, db, path):
    '''Return a tupel (icalendar.Event, datetime.datetime) parsed
       from a locale file or diretory'''

    global forceReload

    if not db.get("eventsByDate") or forceReload:
        forceReload = False
        events      = _parse(path)
        db["times"] = [ x.get("dtstart").dt for x in events ]
        db["eventsByDate"] = events

    return timeframe.selectTimeframe(db["eventsByDate"], db["times"], start, end)

def getEventById(uid, db, path):

    singleFile = os.path.join(path, uid + ".ics")
    if os.path.isfile(singleFile):
        return _parse(singleFile)[0]
    else:
        events = _parse(path)
        for e in events:
            if e["uid"]:
                return e
        raise KeyError("Event not found")
    

def createEvent(event, backendparam):
    global forceReload

    path = backendparam
    cal = icalendar.Calendar()
    cal.add_component(event)

    with open(os.path.join(path, str(event["uid"]) + ".ics"), "wb") as f:
        f.write(cal.to_ical())
        forceReload = True

    return event

def modifyEvent(oldEventID, newEvent, backendparam):
    return createEvent(newEvent, backendparam)

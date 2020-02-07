#!/usr/bin/python3
import os
import re
import uuid

import pytz
import locale
import flask

import icalendar
from datetime import datetime

import utils.timeframe as timeframe
import utils

forceReload = False

def _parseSingleFile(filename):
    '''Read in a single ICS file from a filedescriptor'''

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

    return events

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

    if not db.get("eventsByUID"):
        if db.get("eventsByDate"):
            events = db["eventsByDate"]
        else:
            events = _parse(path)

        # build dict #
        eventDict = dict()
        for e in events:
            eventDict.update({e.get("UID"):e})

        db["eventsByUID"] = eventDict

    return db["eventsByUID"][uid]

def createEvent(title, description, location, startDate, startTime, endDate, endTime, etype=None):

    global forceReload

    INPUT_TIME_FORMAT = "%Y-%m-%d-%H:%M"
    ICAL_TIME_FORMAT  = "%Y%m%dT%H%M%SZ"

    cal = icalendar.Calendar()

    fullStartDateString = "{}-{}".format(startDate, startTime)
    fullEndDateString   = "{}-{}".format(endDate, endTime)

    # generate Event #
    event = icalendar.Event()
    event["uid"] = uuid.uuid4()
    event["dtstart"] = datetime.strptime(fullStartDateString, INPUT_TIME_FORMAT).strftime(ICAL_TIME_FORMAT)
    event["SUMMARY"] = title

    if endDate:
        dtEnd = datetime.strptime(fullEndDateString, INPUT_TIME_FORMAT)
        event["dtend"] = dtEnd.strftime(ICAL_TIME_FORMAT)
    if location:
        event["location"] = location
    if etype:
        event["etype"] = etype
    if description:
        event["DESCRIPTION"] = description

    cal.add_component(event)
    uuidStr = str(event["uid"]) + ".ics"
    with open(os.path.join("data/", uuidStr), "wb") as f:
        f.write(cal.to_ical())
        forceReload = True

    return event

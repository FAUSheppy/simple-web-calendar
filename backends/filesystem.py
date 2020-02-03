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
import utils.parsing   as parsing

forceReload = False

def _parseSingleFile(filename):
    '''Read in a single ICS file from a filedescriptor'''

    with open(filename, 'rb') as f:
        events = []
        gcal = icalendar.Calendar.from_ical(f.read())
        for component in gcal.walk():

            # only select events #
            if type(component) == icalendar.Event:
                events += [component]

                dtLocStart = parsing.localizeDatetime(component.get('dtstart').dt)
                dtLocEndComponent = component.get('dtend')
                component.get("dtstart").dt = dtLocStart

                if dtLocEndComponent:
                    dtLocEnd   = parsing.localizeDatetime(component.get('dtend').dt)
                    component.get("dtend").dt   = dtLocEnd

            else:
                pass

    return events

def _parse(path):

    # get all files to be read #
    srcDir = ""
    if os.path.isdir(path):
        srcDir = path
        files = os.listdir(path)
    else:
        files  = [path]

    # get events from files #
    events = []
    for fname in files:
        if not fname.endswith(".ics"):
            continue
        events += _parseSingleFile(os.path.join(srcDir, fname))

    # link phone numbers #
    for e in events:
        try:
            # phone numbers will be encoded as html, use markup to prevent escaping #
            e['description'] = flask.Markup(parsing.searchAndAmorPhoneNumbers(e['description']))
        except KeyError:
            pass

    # sort events
    return sorted(events, key=lambda x: x.get('dtstart').dt)

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

    cal = icalendar.Calendar()

    # generate Event #
    event = icalendar.Event()
    event["uid"] = uuid.uuid4()
    event["dtstart"] = datetime.strptime(startDate, "%Y-%m-%d").strftime("%Y%m%dT000000Z")
    event["SUMMARY"] = title

    if endDate:
        dtEnd = datetime.strptime(endDate, "%Y-%m-%d")
        event["dtend"] = dtEnd.strftime("%Y%m%dT000000Z")
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

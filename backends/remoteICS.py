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

def _importEvents(url):
    response = requests.request("GET", url)
    events  = utils.parsing.parseEventData(response.text)
    events  = sorted(events, key=lambda x: utils.parsing.localizeDatetime(x.get('dtstart').dt))
    return events

def getEvents(start, end, db, url):
    '''Return a tupel (icalendar.Event, datetime.datetime) parsed
       from a locale file or diretory'''

    global forceReload

    if not db.get("eventsByDate") or forceReload:

        forceReload = False
        events = _importEvents(url)

        db["times"] = [ x.get("dtstart").dt for x in events ]
        db["eventsByDate"] = events

    return timeframe.selectTimeframe(db["eventsByDate"], db["times"], start, end)

def getEventById(uid, db, url):

    if not db.get("eventsByUID"):
        if db.get("eventsByDate"):
            events = db["eventsByDate"]
        else:
            events = _importEvents(url)

        # build dict #
        eventDict = dict()
        for e in events:
            eventDict.update({e.get("UID"):e})

        db["eventsByUID"] = eventDict

    return db["eventsByUID"][uid]

def createEvent(event, backendparam):
    raise AssertionError("Edits not Supportet for this backend.")

def modifyEvent(oldEvent, newEvent, backendparam):
    raise AssertionError("Edits not Supportet for this backend.")

#!/usr/bin/python3
import os
import re

import pytz
import locale
import flask
import flaskext.zodb

import icalendar

import utils.timeframe as timeframe
import utils.parsing   as parsing

def _parseFile(filename):
    '''Read in a single ICS file from a filedescriptor'''

    with open(filename, 'rb') as f:
        events = []
        gcal = icalendar.Calendar.from_ical(f.read())
        for component in gcal.walk():
            
            # only select events #
            if type(component) == icalendar.Event:
                ret += [component]
                dtLocStart = parsing.localizeDatetime(component.get('dtstart').dt)
                dtLocEnd   = parsing.localizeDatetime(component.get('dtend').dt)

                component.get("dtstart").dt = dtLocStart
                component.get("dtend").dt   = dtLocEnd

            else:
                pass

    return events

def getEvents(start, end, dirOrFileName):
    '''Return a tupel (icalendar.Event, datetime.datetime) parsed
       from a locale file or diretory'''
    
    # get all files to be read #
    srcDir = ""
    if os.path.isdir(dirOrFileName):
        srcDir = dirOrFileName
        files = os.listdir(dirOrFileName)
    else:
        files  = [dirOrFileName]
   
    # get events from files #
    events = []
    for fname in files:
        if not f.endswith(".ics"):
            continue
        events += _parseFile(os.path.join(srcDir, fname))

    # link phone numbers
    for e in events:
        try:
            # phone numbers will be encoded as html, use markup to prevent escaping #
            e['description'] = flask.Markup(parsing.searchAndAmorPhoneNumbers(e['description']))
        except KeyError:
            pass

    # sort events
    events = sorted(events, key=lambda x: x.get('dtstart').dt)
    return events

def getEventById(uid, dirOrFileName):
    events = getEvents(None, None, dirOrFileName)
    for e in events:
        if e.get("UID") == uid:
            return e
    return None

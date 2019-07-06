#!/usr/bin/python3
import os
import re

import pytz
import locale

import icalendar

import utils.timeframe as timeframe
import utils.parsing   as parsing

def _parseFile(fd):
    '''Read in a single ICS file from a filedescriptor'''

    ret = []
    gcal = icalendar.Calendar.from_ical(fd.read())
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

    # close file-descriptor #
    fd.close()

    return ret 

def getEvents(start, end, dirOrFileName):
    '''Return a tupel (icalendar.Event, datetime.datetime) parsed
       from a locale file or diretory'''
    
    srcDir = ""
    if os.path.isdir(dirOrFileName):
        srcDir = dirOrFileName
        files = os.listdir(dirOrFileName)
    else:
        files  = [dirOrFileName]
    
    events = []
    for f in files:
        if not f.endswith(".ics"):
            continue
        events += _parseFile(open(os.path.join(srcDir ,f),'rb'))


    # sort events
    events = sorted(events,key=lambda x: x.get('dtstart').dt)

    # link phone numbers
    for e in events:
        try:
            e['description'] = parsing.searchAndAmorPhoneNumbers(e['description'])
        except KeyError:
            pass
    
    # simplify search as we wont change events
    timestamps = [ x.get('dtstart').dt for x in events ]
    return events

def getEventById(uid, dirOrFileName):
    events = getEvents(None, None, dirOrFileName)
    for e in events:
        if e.get("UID") == uid:
            return e
    return None

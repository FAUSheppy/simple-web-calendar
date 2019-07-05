#!/usr/bin/python3
import os
import re

import pytz
import locale

import icalendar

def _parseFile(fd):
    '''Read in a single ICS file from a filedescriptor'''

    ret = []
    gcal = icalendar.Calendar.from_ical(fd.read())
    for component in gcal.walk():
        
        # only select events #
        if type(component) == icalendar.Event:
            ret += [component]
            dtObject = normDT(component.get('dtstart').dt)
        else:
            pass

    # close file-descriptor #
    fd.close()

    return ret 

def getEventTimestampsTupel(dirOrFileName):
    '''Return a tupel (icalendar.Event, datetime.datetime) parsed
       from a locale file or diretory'''

    events = []
    timestamps = []
    
    srcDir = ""
    if os.path.isdir(dirOrFileName):
        srcDir = dirOrFileName
        files = os.listdir(dirOrFileName)
    else:
        files  = [dirOrFileName]

    for f in files:
        if not f.endswith(".ics"):
            continue
        events += _parseFile(open(os.path.join(srcDir ,f),'rb'))


    # sort events
    events = sorted(events,key=lambda x: normDT(x.get('dtstart').dt))

    # link phone numbers
    for e in events:
        try:
            e['description'] = searchAndAmorPhoneNumbers(e['description'])
        except KeyError:
            pass
    
    # simplify search as we wont change events
    timestamps = [ normDT(x.get('dtstart').dt) for x in events ]
    return (events, timestamps)

def getEvents(start, end, dirOrFileName):
    return getEventTimestampsTupel(dirOrFileName)[0]

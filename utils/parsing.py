#!/usr/bin/python3
import re
import bisect
from icalendar import Event, Calendar
from datetime import timedelta, datetime, date, tzinfo
import calendar
import icalendar
import pytz
import unidecode
import locale
import flask

def localizeDatetime(dt):
    '''Make a datetime object timezone localized'''
    if type(dt) == date:
        dtmp = datetime.combine(dt, datetime.min.time())
        return pytz.utc.localize(dtmp, pytz.utc)
    return dt

def searchAndAmorPhoneNumbers(string):
    '''Amor all phone numbers in a string with an HTML-Link'''

    phoneCleaner = str.maketrans(dict.fromkeys('-/ –'))
    counter = 0
    ret = string
    regex = re.compile(r"[-0-9/ ]{7,20}")
    phone_base = "<a class=phone href='tel:{}'>{}</a> "
    tmpString = unidecode.unidecode(string)
    
    for el in list(regex.finditer(tmpString)):
        start = el.regs[0][0]
        end   = el.regs[0][1]
        substr = string[start:end]
        spaces = sum( (" " in s)or("-" in s)or("/" in s) for s in substr)
        
        if len(substr)-spaces < 7:
            continue
        substr = phone_base.format(substr.translate(phoneCleaner),substr)
        ret = ret[:start+counter] + substr + ret[end+counter:]

        #remeber induced offset for removed characters
        counter = len(ret) - len(string)

    # markup special characters  #
    ret = ret.replace("\r", "")
    ret = ret.replace("\n", "<br>")
    ret = ret.replace("\\t", "&nbsp;&nbsp;&nbsp;&nbsp;")

    return ret

def prepareTimeStrings(events, showdate=False):
    preparedTimeStrings = []
    for e in events:
        time = e.get('dtstart').dt
        if type(time) == datetime.date:
            preparedTimeStrings += ["All Day"]
        else:
            preparedTimeStrings += [time.strftime("%H:%M")]

    return preparedTimeStrings

def parseEventData(eventData):
    events = []
    gcal = icalendar.Calendar.from_ical(eventData)
    for component in gcal.walk():
        if type(component) == icalendar.Event:
            events += [component]
            dtLocStart = localizeDatetime(component.get('dtstart').dt)
            dtLocEndComponent = component.get('dtend')
            if dtLocEndComponent:
                dtLocEnd   = localizeDatetime(component.get('dtend').dt)
                component.get("dtend").dt   = dtLocEnd

    # link phone numbers #
    for e in events:
        try:
            # phone numbers will be encoded as html, use markup to prevent escaping #
            e['description'] = flask.Markup(searchAndAmorPhoneNumbers(e['description']))
        except KeyError:
            pass

    return sorted(events, key=lambda x: x.get('dtstart').dt)
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

def buildIcalEvent(title, description, location, startDate, startTime, endDate, endTime, etype=None):
    '''Create an icalendar event'''

    INPUT_TIME_FORMAT = "%Y-%m-%d-%H:%M"
    ICAL_TIME_FORMAT  = "%Y%m%dT%H%M%SZ"

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

    return event

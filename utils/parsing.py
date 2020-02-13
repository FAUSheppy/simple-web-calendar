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
import urllib
import uuid
import dateutil.rrule as rrule

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

def mapLinkFromLocation(location):
    baseUrl = "https://www.google.com/maps/dir/?api=1&destination={}"
    locationAdditive = location.replace(" ","+")
    link = baseUrl.format(urllib.parse.quote(locationAdditive, safe="+"))
    return link

def parseEventData(eventData, start=None, end=None, noAmor=True):
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

    if not noAmor:
        # link phone numbers #
        for e in events:
            try:
                # phone numbers will be encoded as html, use markup to prevent escaping #
                e['description'] = flask.Markup(searchAndAmorPhoneNumbers(e['description']))
            except KeyError:
                pass

    # try to create google maps links #
    for e in events:
        try:
            e.update({"gmaplink":mapLinkFromLocation(e['location'])})
        except KeyError:
            pass

    # fix recurring events #
    if start and end:
        recurringEvents = []
        for e in events:
            ruleInEvent = e.get('rrule')
            if ruleInEvent:
                ruleStr = ruleInEvent.to_ical().decode("utf-8")
                rule = rrule.rrulestr(ruleStr, dtstart=e.get('dtstart').dt)
                recurringEventDates = rule.between(start, end)
                print(recurringEventDates) 

    # filter out original recurring events #
    events = list(filter(lambda e: e.get('rrule'), events))
    print(events)

    return events

def buildIcalEvent(title, description, location, startDate, startTime, endDate, endTime, etype=None, inuid=None):
    '''Create an icalendar event'''

    INPUT_TIME_FORMAT = "%Y-%m-%d-%H:%M"
    ICAL_TIME_FORMAT  = "%Y%m%dT%H%M%SZ"

    fullStartDateString = "{}-{}".format(startDate, startTime)
    fullEndDateString   = "{}-{}".format(endDate, endTime)

    # generate Event #
    event = icalendar.Event()
    if not inuid:
        event["uid"] = uuid.uuid4()
    else:
        event["uid"] = inuid

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

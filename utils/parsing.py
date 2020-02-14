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
    
    # add field lockEdit for all events #
    for e in events:
        try:
            e.update({"lockEdit":False})
        except KeyError:
            pass

    # fix recurring events #
    if start and end:
        recurringEvents = []
        for e in events:
            
            ruleInEvent = e.get('rrule')
            if not ruleInEvent:
                continue

            # decode recurrence rule #
            ruleStr = ruleInEvent.to_ical().decode("utf-8")
            rule = rrule.rrulestr(ruleStr, dtstart=e.get('dtstart').dt)
            
            # get occuring dates in range #
            recurringEventDates = rule.between(start.replace(tzinfo=None), end.replace(tzinfo=None))
            if e.get('dtend'):
                eventLength = e.get('dtend').dt - e.get('dtstart').dt
            else:
                eventLength = datetime.timedelta(seconds=0)

            # create new events for occuring dates #
            for date in recurringEventDates:
                relativeEndDate = date + eventLength
                recurringEvents += [cloneIcalEvent(e, startDatetime=date, endDatetime=relativeEndDate)]

        # add newly generated events #
        if len(recurringEvents) >= 1:
            events += recurringEvents

    # filter out original recurring events #
    events = list(filter(lambda e: not e.get('rrule'), events))
    return events

class PseudeDatetimeComponent:
    def __init__(self, dt):
        self.dt = dt

def cloneIcalEvent(event, startDatetime=None, endDatetime=None):
    
    if not startDatetime:
        startDatetime = event.get("dtstart").dt
    if not endDatetime:
        endDatetime = event.get("dtend").dt
    if not endDatetime:
        endDatetime = startDatetime

    startTime = startDatetime.strftime("%H:%M")
    endTime   = startDatetime.strftime("%H:%M")
    startDate = startDatetime.strftime("%Y-%m-%d")
    endDate   = startDatetime.strftime("%Y-%m-%d")
    event = buildIcalEvent(event.get("SUMMARY"), event.get("DESCRIPTION"), event.get("LOCATION"),
                            startDate, startTime, endDate, endTime, lockEdit=True, inuid=event.get("UID"))

    # fake actualy calendar component #
    event["dtstart"] = PseudeDatetimeComponent(startDatetime.replace(tzinfo=pytz.utc))
    event["dtend"]   = PseudeDatetimeComponent(endDatetime.replace(tzinfo=pytz.utc))
    return event

def buildIcalEvent(title, description, location, startDate, startTime, endDate, endTime, etype=None, inuid=None, lockEdit=False):
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
    
    event["lockEdit"] = lockEdit
    
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

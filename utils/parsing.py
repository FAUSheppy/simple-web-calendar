#!/usr/bin/python3
import re
import bisect
from icalendar import Event, Calendar
from datetime import timedelta, datetime, date, tzinfo
import calendar
import pytz
import unidecode
import locale

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
            isToday = time.date() == datetime.today()
            if isToday or showdate:
                preparedTimeStrings += [time.strftime("%H:%M")]
            else:
                preparedTimeStrings += [time.strftime("%H:%M - %w, %d, %b")]

    return preparedTimeStrings

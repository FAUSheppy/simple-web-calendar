#!/usr/bin/python3
import re
import bisect
from icalendar import Event, Calendar
import calendar
import pytz
import unidecode
import locale

import pwd
import grp
import os

def dayPadding():
    return '<span class="jzdb"><!--BLANK--></span>\n'

def getTargetYearMonth(dt):
    return dt.strftime("%B, %Y")
    
def getDayLink(dt):
    return dt.strftime("dayview?year=%Y&month=%m&day=%-d.html")

def getMonthLink(dt):
    return dt.strftime("monthview?&year=%Y&month=%m.html")

def createSingleDayView(events, timestamps, day, cssDir, jsDir):

    # prepare colums
    completeLeft  = ""
    completeRight = ""

    # prepare templates
    leftItem  = '<div class="rectangle"> <p>{}</p></div>'
    rightItem = '<div class="rectangle"> <p>{}</p> {} </div>'

    # find all relevant events
    selectedEvents = selectTimeframe(events, timestamps, datetime1=day)
    for event in selectedEvents:
        time = event.get('dtstart').dt
        if type(time) == date:
            leftPart = leftItem.format("All day")
        else:
            leftPart = leftItem.format(time.strftime("%H:%M"))
        
        location = event.get('LOCATION')
        hasDescription = event.get('DESCRIPTION')
        if not location:
            location = ""
        if hasDescription:
            description = '</br><a href={}.html>Details</a>'.format(event.get("UID"))
        else:
            description = ""
        buildDescription = "{}\n</br><i>{}</i>".format(event.get('SUMMARY'), location)
        rightPart = rightItem.format(buildDescription, description)
        
        # put it together
        completeLeft  += leftPart
        completeRight += rightPart
    
    # reverse link
    if selectedEvents:
        backLink = getMonthLink(selectedEvents[0].get("dtstart").dt)
    else:
        backLink = "#"

    # format base html
    dateOfView = day.strftime("%A, %d. %B")
    

    nextDayLink = getDayLink(day + timedelta(days=1))
    prevDayLink = getDayLink(day - timedelta(days=1))
    
    return html_base_day.format(cssDir=cssDir, jsDir=jsDir,
                                    nextDay=nextDayLink, prevDay=prevDayLink, \
                                    backLink=backLink, dateOfView=dateOfView, \
                                    left=completeLeft, right=completeRight)


def buildAll(targetDir, cssDir, jsDir):
    global events
    global timestamps

    # build month views
    cur = datetime(timestamps[0].year,timestamps[0].month,1,tzinfo=pytz.utc)
    while cur <= timestamps[-1]:
        oneMonth = timedelta(days=calendar.monthrange(cur.year, cur.month)[1]);

        prevMonth = getMonthLink(cur-timedelta(days=1))
        curMonth  = getTargetYearMonth(cur)
        nextMonth = getMonthLink(cur+oneMonth)

        # build html
        html_full = html_base.format(
                         cssDir, \
                         jsDir,\
                         prevMonth,\
                         curMonth,\
                         nextMonth,\
                         createOverview(\
                              selectTimeframe(events, timestamps, cur, cur+oneMonth),\
                              selectTimeframe(timestamps, timestamps, cur, cur+oneMonth),
                              cur),\
                         )

        fname = targetDir + "/" + getMonthLink(cur)
        with open(fname,"w") as f:
            f.write(html_full)
        fixPermissions(fname, "www-data")
        cur += oneMonth;

    # build day views
    cur = datetime(timestamps[0].year,timestamps[0].month,timestamps[0].day,tzinfo=pytz.utc)
    while cur < timestamps[-1]:
        fname = targetDir + "/" + getDayLink(cur)
        with open(fname,"w") as f:
            outputstring = createSingleDayView(events, timestamps, cur, cssDir, jsDir)
            f.write(outputstring)
        fixPermissions(fname, "www-data")
        cur += timedelta(days=1) 

    for e in events:
        uid = "{}/{}.html".format(targetDir, e.get("UID"))
        backLink = getDayLink(e.get("dtstart").dt)
        with open(uid,"w") as f:
            
            summary = e.get("SUMMARY")
            if not summary:
                summary = "Termin hat keinen Titel - meh"
            
            location    = e.get("LOCATION")
            if not location:
                location = "keine Angabe"
            
            description = e.get("DESCRIPTION")
            if description:
                description = description.replace("\n","\n</br>")

            content = '<b>{}</br></br></b><i>Ort: {}</br></br></i><hr></br><b>Beschreibung:</b></br>{}'
            content = content.format(summary,location,description)
            content = html_base_event.format(cssDir, jsDir, backLink, content)
            f.write(content)
        fixPermissions(uid, "www-data")

html_base = ""
with open("html-snippets/month-view.html") as f:
    html_base = f.read()

html_base_day = ""
with open("html-snippets/day-view.html") as f:
    html_base_day = f.read()

html_base_event = ""
with open("html-snippets/event-view.html") as f:
    html_base_event = f.read()

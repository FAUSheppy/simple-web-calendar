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

def singleOverviewDay(date, hasEvent):
    monthString = date.strftime("%-d")
    if hasEvent:
        html = '<a href={link}> <span id="day-{day}" class="circle">{day}</span> </a>'.format(\
                        link=getDayLink(date), day=date.day)
    else:
        html = '<span id="day-{day}">{day}</span>'.format(day.day)
    return html

def createOverview(events, timestamps, firstDate):

    # preparation
    month   = firstDate.month
    weekday = firstDate.weekday() 
    
    # create padding at start
    padding = ''.join([dayPadding() for x in range(0,weekday)])
    
    # check which days will be highlighted
    exists = dict()
    for t in timestamps:
        if (not t.day in exists) and (t.month == month) and (t.year == firstDate.year):
                exists.update({t.day:t.day})
    
    # create the actual content 
    content = padding

    daysOfMonths = calendar.monthrange(firstDate.year, firstDate.month)[1]
    for x in range(1, daysOfMonths+1):
        content += singleOverviewDay(firstDate.year, firstDate.month, x, x in exists)

    # create padding at end
    needed = (7 - (daysOfMonths + weekday)%7 )%7
    content += ''.join([dayPadding() for x in range(0, needed)])

    return content

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
    
events = []
timestamps = []
def createBase(filename):
    global events
    global timestamps
    
    # set time output language
    try:
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    except locale.Error:
        print("Cannot set custom locale, using system default.")
    
    files = [filename]
    srcDir = ""
    if os.path.isdir(filename):
        srcDir = filename
        files = os.listdir(filename)

    for f in files:
        if not f.endswith(".ics"):
            continue
        #read in file
        events += parseFile(open(os.path.join(srcDir ,f),'rb'))


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

def fixPermissions(fname, group):
    try:
        gid = grp.getgrnam(group).gr_gid
        os.chown(fname,uid=-1,gid=gid)
        os.chmod(fname,0o640)
    except PermissionError:
        pass

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

    # build detail views
    
    
html_base = ""
with open("html-snippets/month-view.html") as f:
    html_base = f.read()

html_base_day = ""
with open("html-snippets/day-view.html") as f:
    html_base_day = f.read()

html_base_event = ""
with open("html-snippets/event-view.html") as f:
    html_base_event = f.read()

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AtlantisHQ CSS Calendar')
    

    parser.add_argument('--icsFile',  help='ICS file to parse')
    parser.add_argument('--url',      help='URL of an supported remote calander')
    parser.add_argument('--radicale', help='Act as a radicale plugin'

    parser.add_argument('--auth-file', defualt="auth.token", help='URL of an supported remote calander')
    parser.add_argument('--targetDir', default="build/", help='Target location of the html files.')
    parser.add_argument('--cssDir',    default="css/", help='Location of the css files')
    parser.add_argument('--jsDir',     default="js/", help='Localtion of the javascript files')
    args = parser.parse_args()

    if args.icsFile:
        createBase(args.icsFile)
        buildAll(args.targetDir,args.cssDir, args.jsDir)
    elif args.url:
        pass
    elif args.radicale:
        pass
    else:
        raise NotImplementedError() 

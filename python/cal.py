#!/usr/bin/python3
import re
import bisect
from icalendar import Event, Calendar
from datetime import timedelta, datetime, date, tzinfo
import calendar
import pytz
import locale

import pwd
import grp
import os

def normDT(dt):
    if type(dt) == date:
        dtmp = datetime.combine(dt, datetime.min.time())
        return pytz.utc.localize(dtmp,pytz.utc)
    return dt

def phoneRecogAudit(substr):
    spaces = sum(" " in s for s in substr)
    if len(substr)-spaces >= 7:
        print("Accepted: '{}'".format(substr))
        return
    new = substr.strip(" ")
    if len(new) > 0:
        print("                                   Discarded: '{}'".format(substr))

phoneCleaner = str.maketrans(dict.fromkeys('-/ '))
def searchAndAmorPhoneNumbers(string):
    counter = 0
    ret = string
    regex = re.compile(r"[-0-9/ ]{7,20}")
    phone_base = "<a class=phone href='tel:{}'>{}</a> "
    for el in list(regex.finditer(string)):
        start = el.regs[0][0]
        end   = el.regs[0][1]
        substr = string[start:end]
        spaces = sum( (" " in s)or("-" in s)or("/" in s) for s in substr)
        
        # debug #
        #phoneRecogAudit(substr)
        
        if len(substr)-spaces < 7:
            continue
        substr = phone_base.format(substr.translate(phoneCleaner),substr)
        ret = ret[:start+counter] + substr + ret[end+counter:]

        #remeber induced offset
        counter = len(ret) - len(string)
    return ret

def parseFile(g):
    ret = []
    gcal = Calendar.from_ical(g.read())
    for component in gcal.walk():
        
        # only want events
        if type(component) == Event:
            ret += [component]
            dtObject = normDT(component.get('dtstart').dt)
        else:
            pass

    # close file
    g.close()

    # make sure events are in order
    return ret 

def selectTimeframe(events, timestamps, datetime1,datetime2=None):
    if not datetime2:
        datetime2 = datetime1 + (timedelta(days=1) - timedelta(seconds=1))

    start = bisect.bisect_left(timestamps, datetime1 )
    end   = bisect.bisect_right(timestamps, datetime2 )
    return events[start:end]
        
def dayPadding():
    return '<span class="jzdb"><!--BLANK--></span>\n'

def getTargetYearMonth(dt):
    return dt.strftime("%B, %Y")
def getDayLink(dt):
    return dt.strftime("day-%Y&%m&%-d.html")
def getMonthLink(dt):
    return dt.strftime("month-%Y&%m.html")

def singleOverviewDay(year, month, numberOfDay, hasEvent):
    if month < 10:
        month = "0{}".format(month)
    dayId = "day-{}".format(numberOfDay)
    if hasEvent:
        link = 'day-{}&{}&{}.html'.format(year, month, numberOfDay)
        html = '<a href={}> <span id="{}" class="circle">{}</span> </a>'.format(\
                        link, dayId, numberOfDay)
    else:
        html = '<span id="{}">{}</span>'.format(dayId, numberOfDay)
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
    return html_base_day.format(cssDir, jsDir, backLink, dateOfView, completeLeft, completeRight)
    
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
            #outputstring = searchAndAmorPhoneNumbers(outputstring)
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
            #content = searchAndAmorPhoneNumbers(content)
            f.write(content)
        fixPermissions(uid, "www-data")

    # build detail views
    
    
html_base = '''
<!DOCTYPE html>
<html lang="en" >
  <head>
    <meta charset="UTF-8">
      <title>ATHQ</title>
      <link rel="stylesheet" href="{}/month.css">
      <script defer src="{}/site.js"></script>
  </head>
  <body>
    <div id="offlineInfo"><b>OFFLINE MODUS</b></div>    
    <div class="jzdbox1 jzdbasf jzdcal">
    <div class="headerbar">
        <div class="jzdcalt prev">
            <a class="bigLink" href={}>&laquo;&laquo;</a>    
        </div>
        <div class="jzdcalt">{}</div>
        <div class="jzdcalt next">
            <a class="bigLink" href={}>&raquo;&raquo;</a>
        </div>
    </div>
      <span>Mo</span>
      <span>Di</span>
      <span>Mi</span>
      <span>Do</span>
      <span>Fr</span>
      <span>Sa</span>
      <span>So</span>
      {}
    <div class="vspace">
        &nbsp; </br>
    </div>
    <div class="currentDate" id="time">
          Datum/Uhrzeit nicht verfügbar.
    </div>
    </div>
  </body>
</html>
'''

html_base_day = '''
<!DOCTYPE html>
<html lang="en" >
  <head>
    <meta charset="UTF-8">
    <title>ATHQ-single</title>
    <link rel="stylesheet" href="{}/day.css">
    <script defer src="{}/site.js"></script>
  </head>
  <body>
    <div id="offlineInfo"><b>OFFLINE MODUS</b></div>    
    <div class="menubar">                                                                           
        <a class=menubarLink href="{}"> &laquo &laquo Monatsübersicht &laquo &laquo </a>
    </div>
    <div class="menubarDate" id="menubarDate">
        <class=currentDate style="font-size: 5vw;">{}</a>
    </div>
    <div class="row">
        <div class="column1">
            {}
        </div>
        <div class="column2">
            {}
        </div>
    </div>
  </body>
</html>
'''

html_base_event = '''
<!DOCTYPE html>
<html lang="en" >
  <head>
    <meta charset="UTF-8">
    <title>ATHQ-single</title>
    <link rel="stylesheet" href="{}/day.css">
    <script defer src="{}/site.js"></script>
  </head>
  <body>
    <div id="offlineInfo"><b>OFFLINE MODUS</b></div>    
    <div class="menubar">                                                                           
        <a class=menubarLink href="{}"> &laquo &laquo Tagesübersicht &laquo &laquo </a>
    </div>
      <div class="eventview">
            {}
      </div>
    </div>
  </body>
</html>
'''

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AtlantisHQ CSS Calendar')
    parser.add_argument('icsFile', type=str, help='ics file to parse')
    parser.add_argument('targetDir', type=str, help='ics file to parse')
    parser.add_argument('cssDir', type=str, help='ics file to parse')
    parser.add_argument('jsDir', type=str, help='ics file to parse')
    args = parser.parse_args()
    createBase(args.icsFile)
    buildAll(args.targetDir,args.cssDir, args.jsDir)

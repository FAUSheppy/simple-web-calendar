#!/usr/bin/python3
import bisect
from icalendar import Event, Calendar
from datetime import timedelta, datetime, date, tzinfo
import calendar
import pytz

def normDT(dt):
    if type(dt) == date:
        dtmp = datetime.combine(dt, datetime.min.time())
        return pytz.utc.localize(dtmp,pytz.utc)
    return dt

def parseFile(g):
    ret = []
    gcal = Calendar.from_ical(g.read())
    for component in gcal.walk():
        
        # only want events
        if type(component) == Event:
            ret += [component]
            dtObject = normDT(component.get('dtstart').dt)

    # close file
    g.close()

    # make sure events are in order
    return sorted(ret,key=lambda x: normDT(x.get('dtstart').dt))

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

def singleOverviewDay(year, month, numberOfDay, hasEvent):
    if hasEvent:
        link = 'day-{}&{}&{}.html'.format(year,month,numberOfDay)
        html = '<a href={}> <span class="circle">{}</span> </a>'.format(link,numberOfDay)
    else:
        html = '<span>{}</span>'.format(numberOfDay)
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
        if (not t.day in exists) and (t.month == month):
                exists.update({t.day:t.day})
    
    # create the actual content 
    content = padding

    daysOfMonths = calendar.monthrange(firstDate.year, firstDate.month)[1]
    for x in range(1, daysOfMonths+1):
        content += singleOverviewDay(firstDate.year, firstDate.month, x, x in exists)

    # create padding at end
    content += ''.join([dayPadding() for x in range(0, 7-(daysOfMonths + weekday)%7)])

    return content

def createSingleDayView(events, timestamps, day, cssDir):

    # prepare colums
    completeLeft  = ""
    completeRight = ""

    # prepare templates
    leftItem  = '<div class="rectangle"> <p>{}</p> </div>'
    rightItem = '<div class="rectangle"> <p>{}</p> </div>'

    # find all relevant events
    selectedEvents = selectTimeframe(events, timestamps, datetime1=day)
    for event in selectedEvents:
        time = event.get('dtstart').dt
        if type(time) == date:
            leftPart = leftItem.format("All day")
        else:
            leftPart = leftItem.format(time.strftime("%H:%M"))
        
        location = event.get('LOCATION')
        if not location:
            location = ""
        buildDescription = "{}\n</br>{}".format(event.get('SUMMARY'),location)
        rightPart = rightItem.format(buildDescription)
        
        # put it together
        completeLeft  += leftPart
        completeRight += rightPart

    # format base html
    return html_base_day.format(cssDir, completeLeft,completeRight)
    
events = None
timestamps = None
def createBase(filename):
    global events
    global timestamps

    #read in file
    events = parseFile(open(filename,'rb'))

    # simplify search as we wont change events
    timestamps = [ normDT(x.get('dtstart').dt) for x in events ]

def buildAll(targetDir, cssDir):
    global events
    global timestamps

    # build month views
    cur = datetime(timestamps[0].year,timestamps[0].month,1,tzinfo=pytz.utc)
    while cur <= timestamps[-1]:
        oneMonth = timedelta(days=calendar.monthrange(cur.year, cur.month)[1]);
        # build html
        html_full = html_base.format(cssDir, getTargetYearMonth(cur),\
                         createOverview(selectTimeframe(events, timestamps, cur, cur+oneMonth),\
                         timestamps, cur))
        fname = "{}/month-{}&{}.html".format(targetDir,cur.year,cur.month)
        with open(fname,"w") as f:
            f.write(html_full)
        cur += oneMonth;

    # build day views
    cur = datetime(timestamps[0].year,timestamps[0].month,timestamps[0].day,tzinfo=pytz.utc)
    while cur < timestamps[-1]:
        fname = "{}/day-{}&{}&{}.html".format(targetDir, cur.year,cur.month, cur.day)
        with open(fname,"w") as f:
            f.write(createSingleDayView(events, timestamps, cur, cssDir))
        cur += timedelta(days=1) 
    
html_base = '''
<!DOCTYPE html>
<html lang="en" >
  <head>
    <meta charset="UTF-8">
      <title>ATHQ</title>
      <link rel="stylesheet" href="{}/month.css">
  </head>
  <body>
    <div class="jzdbox1 jzdbasf jzdcal">
    <div class="jzdcalt">{}</div>
      <span>Mo</span>
      <span>Tu</span>
      <span>We</span>
      <span>Th</span>
      <span>Fr</span>
      <span>Sa</span>
      <span>Su</span>
      {}
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
  </head>
  <body>
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

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AtlantisHQ CSS Calendar')
    parser.add_argument('icsFile', type=str, help='ics file to parse')
    parser.add_argument('targetDir', type=str, help='ics file to parse')
    parser.add_argument('cssDir', type=str, help='ics file to parse')
    args = parser.parse_args()
    createBase(args.icsFile)
    buildAll(args.targetDir,args.cssDir)

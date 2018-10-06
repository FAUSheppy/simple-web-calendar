#!/usr/bin/python3
import bisect
from icalendar import Event, Calendar
from datetime import timedelta
import calendar

def parseFile(g)
		ret = []
		gcal = Calendar.from_ical(g.read())
		for component in gcal.walk():
				
				# only want events
				if type(component) == Event:
						ret += [component]

		# close file
		g.close()

		# make sure events are in order
		return sorted(ret,key=lambda x: x.get('dtstart').dt)

def selectTimeframe(events, timestamps, datetime1,datetime2):
		if not datetime2:
				datetime2 = datetime1 + (timedelta(days=1) - timedelta(seconds=1))

		start = bisect.bisect_right( timestamps, datetime1 )
		end   = bisect.bisect_left(  timestamps, datetime2 )

		return events[start:end]
				
def dayPadding(events):
		return '<span class="jzdb"><!--BLANK--></span>\n'

def getTargetYearMonth(events):
		return events[0].get('dtstart').dt.strftime("%B, %Y")

def singleOverviewDay(numberOfDay, hasEvent):
		if hasEvent:
				html = '<a href={} <span class="circle">{}</span> </a>'.format(numberOfDay)
		else:
				html = '<span class="circle">{}</span>'.format(numberOfDay)
		return html

def createOverview(events, timestamps):

		# preparation
		firstDate = events[0].get('dtstart').dt
		month   = firstDate.month
		weekday = firstDate.weekday()	
		
		# create padding at start
		padding = ''.join([dayPadding() for x in range(0,weekday)])
		
		# check which days will be highlighted
		exists = dict()
		for t in timestamps:
				if (not t.day in exists) and (t.month == month):
						exists.update(t.day,t.day)
		
		# create the actual content	
		content = ""
		daysOfMonths = calendar.monthrange(firstDate.year, firstDate.month)[1]
		for x in range(1, daysOfMonths+1):
				content += singleOverviewDay(x,x in exists)
		return content

def createSingleDayView(events, day):
		pass

def createBase(filename):
		#read in file
		events = parseFile(open(filename,'rb'))

		# simplify search as we wont change events
		timestamps = [ x.get('dtstart').dt for x in events ]

		# build html
		html_full = html_base.format(getTargetYearMonth(),createOverview())

		with open("test.html","w") as f:
				f.write(html_full)

html_base = '
<!DOCTYPE html>
<html lang="en" >
	<head>
  	<meta charset="UTF-8">
  	<title>ATHQ</title>
		<link rel="stylesheet" href="css/style.css">
	</head>
	<body>
  	<div class="jzdbox1 jzdbasf jzdcal">
		<div class="jzdcalt">{}</div>
			<span>Su</span>
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
</html>'

createBase("test.ics")

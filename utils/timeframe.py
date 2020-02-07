#!/usr/bin/python3
import bisect
from datetime import datetime, timedelta
import utils

def currentDay():
    return datetime(timestamps[0].year,timestamps[0].month,1,tzinfo=pytz.utc)

def selectTimeframe(events, times, start, end):
    '''Bisect a timeframe for a sorted list of events'''
    
    localizedTimes = [ utils.parsing.localizeDatetime(x) for x in times ]

    start = bisect.bisect_left(localizedTimes, start)
    end   = bisect.bisect_right(localizedTimes, end)

    return events[start:end]

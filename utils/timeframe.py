#!/usr/bin/python3
import bisect
from datetime import datetime, timedelta

def currentDay():
    return datetime(timestamps[0].year,timestamps[0].month,1,tzinfo=pytz.utc)

def selectTimeframe(events, times, start, end):
    '''Bised a timeframe for a sorted list of events'''
    
    start = bisect.bisect_left(  times, start)
    end   = bisect.bisect_right( times, end)

    return events[start:end]

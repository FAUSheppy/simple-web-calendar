#!/usr/bin/python3
import bisect
from datetime import datetime, timedelta

def currentDay():
    return datetime(timestamps[0].year,timestamps[0].month,1,tzinfo=pytz.utc)

def selectTimeframe(events, timestamps, datetime1, datetime2=None):
    if not datetime2:
        datetime2 = datetime1 + (timedelta(days=1) - timedelta(seconds=1))
    start = bisect.bisect_left(timestamps, datetime1 )
    end   = bisect.bisect_right(timestamps, datetime2 )
    return events[start:end]

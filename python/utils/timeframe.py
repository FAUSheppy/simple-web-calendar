#!/usr/bin/python3
import bisect

def selectTimeframe(events, timestamps, datetime1, datetime2=None):
    if not datetime2:
        datetime2 = datetime1 + (timedelta(days=1) - timedelta(seconds=1))
    start = bisect.bisect_left(timestamps, datetime1 )
    end   = bisect.bisect_right(timestamps, datetime2 )
    return events[start:end]

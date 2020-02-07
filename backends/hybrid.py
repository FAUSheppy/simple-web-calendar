#!/usr/bin/python3
import backends.remoteICS  as remote
import backends.filesystem as locale

def getEvents(start, end, db, backendparam):
        path, url, authFile = backendparam
        return locale.getEvents(start, end, db, path)

def getEventById(uid, db, backendparam):
        path, url, authFile = backendparam
        return locale.getEventById(uid, pd, path)

def createEvent(title, description, location, startDate, \
                    startTime, endDate, endTime, etype=None, backendparam=None):
        path, url, authFile = backendparam
        event = remote.writeEvent(title, description, location, startDate,\
                                    startTime, endDate, endTime, etype, (url, authFile))
        return event

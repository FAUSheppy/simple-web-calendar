#!/usr/bin/python3
import backends.remoteCaldav as remote
import backends.filesystem   as locale

def getEvents(start, end, db, backendparam):
    path, url, user, pw = backendparam
    return remote.getEvents(start, end, db, (url, user, pw))

def getEventById(uid, db, backendparam, noAmor=False):
    path, url, user, pw = backendparam
    return locale.getEventById(uid, db, path, noAmor)

def createEvent(event, backendparam):
    path, url, user, pw = backendparam
    event = remote.createEvent(event, (url, user, pw))
    return event

def modifyEvent(oldEventId, newEvent, backendparam):
    path, url, user, pw = backendparam
    event = remote.modifyEvent(oldEventId, newEvent, (url, user, pw))
    return event

#!/usr/bin/python3
import backends.remoteCaldav as remote
import backends.filesystem   as locale

def getEvents(start, end, db, backendparam):
    path, url, user, pw = backendparam
    return locale.getEvents(start, end, db, path)

def getEventById(uid, db, backendparam, noAmor=True):
    path, url, user, pw = backendparam
    return locale.getEventById(uid, db, path)

def createEvent(event, backendparam):
    path, url, user, pw = backendparam
    event = remote.createEvent(event, (url, user, pw))
    return event

def modifyEvent(oldEvent, newEvent, backendparam, noAmor=False):
    path, url, user, pw = backendparam
    event = remote.modifyEvent(event, (url, user, pw))
    return event

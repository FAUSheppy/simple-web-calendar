import googleapiclient.discovery      as g_api
import google_auth_oauthlib.flow      as g_auth
import google.auth.transport.requests as g_transport
import datetime

def getEvents(start, end, db, backendparams):

    if db and db["lastupdate"] + datetime.timedelta(minutes=1) > datetime.now():
        return db["eventsByDate"] = events

    url, authFile = backendparams
    calConnector = g_api.build('calendar', 'v3', credentials=authFile) # actualy calender defined in auth File
    events = calConnector.events().list(calendarId='primary', timeMin=start, timeMax=end \
                                        maxResults=100, singleEvents=True, \
                                        orderBy='startTime').execute()

    events = events.get("items", []) # get actual event items form response

    db["times"] = [ x.get("dtstart").dt for x in events ]
    db["eventsByDate"] = events
    db["lastupdate"]   = datetime.now()

    return db["eventsByDate"]

def getEventById(uid, db, backendparams):
    url, authFile = backendparams

    calConnector = g_api.build('calendar', 'v3', credentials=authFile) # actualy calender defined in auth File
    event = calConnector.events().get(calendarId='primary', eventId=uid).execute()
    if not event:
        raise ValueError("No event by this ID, might have been deleted. ID: {}".format("uid"))

    return event


def createEvent(title, description, location, startDate, startTime, endDate, endTime, etype=None, backendparams=None):
    raise NotImplementedError()

import icalendar
import caldav

def createEvent((title, description, location, startDate, startTime, endDate, endTime, backendparam, etype=None):
    url      = "http://test.com"
    username = "TEST"
    password = "PASS"
    client = caldav.DAVClient(url=url, username=username, password=password)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    calendar.add_event(event)
    return event

def getEventById(uid, db, backendparam):
    raise NotImplementedError()

def getEvents(start, end, db, backendparam)
    raise NotImplementedError()

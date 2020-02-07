import caldav
import utils.parsing

def createEvent(event, backendparam):
    url, user, pw = backendparam
    client = caldav.DAVClient(url=url, username=user, password=pw)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    calendar.add_event(event)
    return event

def getEventById(uid, db, backendparam):
    url, user, pw = backendparam
    client = caldav.DAVClient(url=url, username=user, password=pw)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    return utils.parsing.parseEventData(defaultCal.event_by_uid(uid).data)

def getEvents(start, end, db, backendparam):
    url, user, pw = backendparam
    client = caldav.DAVClient(url=url, username=user, password=pw)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    unparsedEvents = defaultCal.date_search(start, end)
    returnEvents = []
    for event in unparsedEvents:
        returnEvents += utils.parsing.parseEventData(event.data)
    print(returnEvents[0])
    return returnEvents

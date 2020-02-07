import caldav
import utils.parsing
import icalendar

def createEvent(event, backendparam):
    url, user, pw = backendparam
    client = caldav.DAVClient(url=url, username=user, password=pw)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    dummyCal = icalendar.Calendar()
    dummyCal.add_component(event)
    defaultCal.add_event(dummyCal.to_ical())
    return event

def getEventById(uid, db, backendparam):
    url, user, pw = backendparam
    client = caldav.DAVClient(url=url, username=user, password=pw)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    events = utils.parsing.parseEventData(defaultCal.event_by_uid(uid).data)
    if len(events) != 1:
        raise ValueError("UID query return more than one event.")
    return events[0]

def getEvents(start, end, db, backendparam):
    url, user, pw = backendparam
    client = caldav.DAVClient(url=url, username=user, password=pw)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    unparsedEvents = defaultCal.date_search(start, end)
    returnEvents = []
    for event in unparsedEvents:
        returnEvents += utils.parsing.parseEventData(event.data)
    return sorted(returnEvents, key=lambda x: utils.parsing.localizeDatetime(x.get('dtstart').dt))

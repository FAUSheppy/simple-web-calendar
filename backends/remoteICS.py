import icalendar
import caldav

def writeEventToRemote(url, event):
    url      = "http://test.com"
    username = "TEST"
    password = "PASS"
    client = caldav.DAVClient(url=url, username=username, password=password)
    authenticatedClient = client.principal()
    defaultCal = authenticatedClient.calendars()[0]
    calendar.add_event(event)

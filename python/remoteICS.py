import googleapiclient.discovery      as g_api
import google_auth_oauthlib.flow      as g_auth
import google.auth.transport.requests as g_transport

def syncPullGoogle(url, cerdentials="", maxEvents=100):
    calConnector = g_api.build('calendar', 'v3', credentials=creds)

    # 'Z' indicates UTC time
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    events = calConnector.events().list(calendarId='primary', timeMin=now, \
                                        maxResults=maxResults, singleEvents=True, \
                                        orderBy='startTime').execute()
    
    return events.get("items", [])
    

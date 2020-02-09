# Introduction
This [flask-Server](https://www.palletsprojects.com/p/flask/) takes a calendar backend, either as a remote ICS file (e.g. Google-Calendar), a CalDav-Server (e.g. Radicale or OwnCloud), or a local directory. It can also run in hybrid mode when on the same filesystem as a [Radical-Server](https://radicale.org/) or any CalDav-Server supporting filesystem as storrage. It will read events by their UID from the filesystem, but query the CalDav/Radicale server for date-ranges and edits. This is primarily a workaround until radicale correctly implements `get_event_by_uuid`.

# Live Demo
A live demo filled with data from random events in Frankfurt can be found on [demo-calendar.atlantishq.de](https://demo-calendar.atlantishq.de). 

# Usage

    usage: server.py [-h] [-i INTERFACE] [-p PORT] [-b BACKEND] [--locale-de]
                     [--auth-file AUTH_FILE] [--remote-url REMOTE_URL]
                     [--fs-backend-path FS_BACKEND_PATH] [--read-only]
    
    Calender webfront and gateway
    
    optional arguments:
      -h, --help            show this help message and exit
      -i INTERFACE, --interface INTERFACE
                            Interface to listen on (default: 0.0.0.0)
      -p PORT, --port PORT  Port to listen on (default: 5000)
      -b BACKEND, --backend BACKEND
                            fileystem|caldav|remoteics|hybrid (default:
                            filesystem)
      --locale-de           Use german localization for dates etc. (default: None)
      --auth-file AUTH_FILE
                            Authentication file for backend (caldav/hybrid)
                            (default: None)
      --remote-url REMOTE_URL
                            Remote url (caldav/hybrid) (default: None)
      --fs-backend-path FS_BACKEND_PATH
                            Path for locale directory (filesystem/hybrid)
                            (default: data)
      --read-only           Disable editing the calendar (reply 401 in API and disable buttons) (default: False)

# Future Features planned
* Offline Support with ServiceWorker

# Pictures
## Month View/Main View
![month view](https://media.atlantishq.de/month-view.png)

## Single-Day View
![day view](https://media.atlantishq.de/day-view.png)

## Single-Event/Detailed View
![single event view](https://media.atlantishq.de/event-view.png)

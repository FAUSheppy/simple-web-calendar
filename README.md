# Introduction
This script can create static web-pages from any ICS-calendar file. It's original purpose was to be used as a read only calendar on mobile devices in conjunction with the [radicale calendar backend](https://radicale.org/). It is still in active development.

# Live Demo
A live demo filled with data from random events in Frankfurt can be found on [demo-calendar.atlantishq.de](demo-calendar.atlantishq.de). 

# Usage

    usage: server.py [-h] [-i INTERFACE] [-p PORT] [-b BACKEND]
                     [--auth-file AUTH_FILE] [--remote-url REMOTE_URL]
                     [--fs-backend-path FS_BACKEND_PATH]
    
    Start calendar server.
    
    optional arguments:
      -h, --help            show this help message and exit
      -i INTERFACE, --interface INTERFACE
                            Interface to listen on (default: 0.0.0.0)
      -p PORT, --port PORT  Port to listen on (default: 5000)
      -b BACKEND, --backend BACKEND
                            Backend to use (default: filesystem)
      --auth-file AUTH_FILE
                            Auth file for backend if necessary (default:
                            auth.token)
      --remote-url REMOTE_URL
                            Remote url when using backend remote or google
                            (default: None)
      --fs-backend-path FS_BACKEND_PATH
                            Path for locale file if backend 'filesystem' is used
                            (default: data)


# Future Features planned
* client side javascript to modify calendar entries
* radicale web integration

# Pictures
## Month View/Main View
![month view](https://media.atlantishq.de/month-view.png)

## Single-Day View
![day view](https://media.atlantishq.de/day-view.png)

## Single-Event/Detailed View
![single event view](https://media.atlantishq.de/event-view.png)

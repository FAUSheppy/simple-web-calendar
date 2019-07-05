#!/usr/bin/python3

import flask
import sys

import backends.filesystem
import utils.timeframe
import argparse

backend = backends.filesystem
backendparam = "./data/"

app = flask.Flask("epic-open-calendar-frontend")

@app.route("/monthview")
def monthView():
    month = int(flask.request.get("month"))
    year  = int(flask.request.get("year"))
    daysInMonth = calendar.monthrange(year, month)[1]

    start = datetime(year, month, day=1, tzinfo=pytz.utc)
    end   = datetime(year, month + 1, tzinfo=pytz.utc) - timedelta(milliseconds=1)

    events = backend.getEvents(start, end, backendparam)
    
    # mark all days with event #
    eventsOnDay = [ False for x in range(0, daysInMonth)]
    for e in events:
        eventsOnDay[events.get('dtstart').dt.day % daysInMonth] = True

    # generate navigation links
    hrefPrevMonth = ""
    hrefCurrMonth = ""
    hrefNextMonth = ""

    return flask.render_template("month-view-mobile.html", \
                                        year=year, \
                                        month=month, \
                                        eventsOnDay=eventsOnDay, \
                                        hrefPrevMonth=hrefPrevMonth, \
                                        hrefNextMonth=hrefNextMonth, \
                                        hrefCurrent=hrefCurrMonth, \
                                        paddingStart=start.weekday(), \
                                        paddingEnd=(7 - (daysInMonths + start.weekday())%7 )%7)

@app.route("/dayview")
def dayView():
    day   = flask.request.get("day")
    month = flask.request.get("month")
    year  = flask.request.get("year")

    return flask.render_template()

@app.route("/eventview")
def eventView():
    events, timestamps = backend.getEvents(start, end, icsDataPath)
    

    return ""

@app.route("/static/<path:path>")
def sendStatic(path):
    return flask.send_from_directory('static', path)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Start open-leaderboard',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general parameters #
    parser.add_argument("-i", "--interface", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("-p", "--port",      default="5000", help="Port to listen on")
    parser.add_argument("-b", "--backend",   default="filesystem", help="Backend to use")

    # backend specific parameters #
    parser.add_argument("--auth-file", default="auth.token", \
                            help="Auth file for backend if nessesary")
    parser.add_argument("--remote-url", default=None, \
                            help="Remote url when using backend remote or google")
    parser.add_argument("--fs-backend-path", default="data", \
                            help="Path for locale file if backend 'filesystem' is used")
    
    args = parser.parse_args()

    #  set backend #
    if args.backend == "filesystem":
        backend = backends.filesystem
        icsDataPath = args.fs_backend_path
    else:
        print("Unsupportet backend", file=sys.stderr)
        sys.exit(1)

    #  set backend variables #


    # startup #
    args = parser.parse_args()
    app.run(interface=args.interface, port=args.port)

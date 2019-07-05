#!/usr/bin/python3

import flask

import sys
import argparse

import backends.filesystem
import utils.timeframe

import datetime
import calendar
import pytz

backend = backends.filesystem
backendparam = "./data/"

app = flask.Flask("epic-open-calendar-frontend")

oneMillisecond  = datetime.timedelta(milliseconds=1)

@app.route("/")
def htmlRedirect():
    # do html redirect because some browsers (i.e. safari) #
    # will not let you bookmark a page that returns 30X :( #
    return flask.render_template("redirectRoot.html", dt=datetime.datetime.now())

@app.route("/monthview")
def monthView():
    month = int(flask.request.args.get("month"))
    year  = int(flask.request.args.get("year"))

    start  = datetime.datetime(year, month,     day=1, tzinfo=pytz.utc)
    end    = datetime.datetime(year, month + 1, day=1, tzinfo=pytz.utc) - oneMillisecond

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
    app.run(host=args.interface, port=args.port)

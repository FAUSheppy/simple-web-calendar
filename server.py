#!/usr/bin/python3

import flask

import sys
import argparse
import locale

import backends.filesystem
import backends.hybrid
import backends.remoteCaldav
import backends.remoteICS
import utils.timeframe

import datetime
import dateutil.relativedelta
import dateutil.tz
import calendar
import pytz
import json
import os

import flask_caching as fcache

backend = backends.filesystem
backendparam = None
READ_ONLY = False

app = flask.Flask("epic-open-calendar-frontend")
cache = fcache.Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

db  = dict()

oneMillisecond  = datetime.timedelta(milliseconds=1)
oneMonth        = dateutil.relativedelta.relativedelta(months=1)
oneWeek         = dateutil.relativedelta.relativedelta(days=7)
oneDay          = dateutil.relativedelta.relativedelta(days=1)

# prefomated links #
dayLinkFormatString   = "/dayview?year={}&month={}&day={}"
monthLinkFormatString = "/monthview?year={}&month={}"

# constants #
SELECT_DAY_OF_WEEK = 2


@app.route("/")
def htmlRedirect():
    # do html redirect because some browsers (i.e. safari) #
    # will not let you bookmark a page that returns 30X :( #
    return flask.render_template("redirectRoot.html", dt=datetime.datetime.now())

@app.route("/monthview")
@cache.cached(timeout=7200, query_string=True)
def monthView():
    month = int(flask.request.args.get("month"))
    year  = int(flask.request.args.get("year"))

    start  = datetime.datetime(year, month, day=1, tzinfo=pytz.utc)
    end    = start + oneMonth - oneMillisecond

    prevMonth = start - oneMonth
    nextMonth = start + oneMonth
    
    events = backend.getEvents(start, end, db, backendparam)
    
    # mark all days with event #
    firstDayWeekdayCount, totalDaysInMonth = calendar.monthrange(year, month)
    
    # totalDaysInMonth - 1 to create 0-indexed array #
    eventsOnDay = [ False for x in range(0, totalDaysInMonth)]
    for e in events:
        eventsOnDay[(e.get('dtstart').dt.day % totalDaysInMonth) - 1] = True

    # generate navigation links
    hrefPrevMonth = monthLinkFormatString.format(prevMonth.year, prevMonth.month)
    hrefNextMonth = monthLinkFormatString.format(nextMonth.year, nextMonth.month)

    weekDayPaddingEnd = (7 - (totalDaysInMonth + firstDayWeekdayCount)%7 )%7

    now = datetime.datetime.now()
    today = datetime.datetime(year=now.year, month=now.month, day=now.day).replace(tzinfo=dateutil.tz.tzlocal())
    tomorrow = today + datetime.timedelta(hours=23, minutes=59, seconds=59)

    events              = backend.getEvents(today, tomorrow, db, backendparam)
    preparedTimeStrings = utils.parsing.prepareTimeStrings(events)
    todayView           = flask.Markup(flask.render_template('partials/eventRow.html', events=events, preparedTimeStrings=preparedTimeStrings))

    return flask.render_template("month-view-mobile.html", \
                                        year=year, \
                                        month=month, \
                                        eventsOnDay=eventsOnDay, \
                                        hrefPrevMonth=hrefPrevMonth, \
                                        hrefNextMonth=hrefNextMonth, \
                                        currentMonthString=start.strftime("%B"), \
                                        paddingStart=firstDayWeekdayCount, \
                                        paddingEnd=weekDayPaddingEnd, \
                                        todayView=todayView, \
                                        readonly=READ_ONLY)

@app.route("/weekview")
@cache.cached(timeout=7200, query_string=True)
def weekView():
    day   = flask.request.args.get("day")
    month = int(flask.request.args.get("month"))
    year  = int(flask.request.args.get("year"))

    # select first day in month if arg is missing #
    if not day:
        day = 1
    else:
        day = int(day)

    selected    = datetime.datetime(year, month, day, tzinfo=pytz.utc)
    startOfWeek = selected - datetime.timedelta(days=selected.isocalendar()[SELECT_DAY_OF_WEEK])
    end         = startOfWeek + oneWeek - oneMillisecond

    prevDay = "NOT IMPLEMENTED"
    nextDay = "NOT IMPLEMENTED"

    hrefPrevDay   = "NOT IMPLEMENTED"
    hrefNextDay   = "NOT IMPLEMENTED"
    hrefThisMonth = "NOT IMPLEMENTED"

    dateOfViewString = "NOT IMPLEMENTED"

    # get locale week names #
    weekdayNames = ["BUFFER"] + list(calendar.day_name)

    events = backend.getEvents(startOfWeek, end, db, backendparam)

    # create event lists for each day #
    weekEventLists = [ list() for x in range(0, 7) ]
    for e in events:
        weekEventLists[e.get('dtstart').dt.isocalendar()[SELECT_DAY_OF_WEEK]-1] += [e]

    return flask.render_template("week-view.html", weekEventLists=weekEventLists, \
                                    weekdayNames=weekdayNames, \
                                    preparedTimeStrings="NOT IMPLEMENTED", \
                                    prevDayLink=hrefPrevDay, \
                                    nextDayLink=hrefNextDay, \
                                    thisMonthLink=hrefThisMonth, \
                                    dateOfView=dateOfViewString, \
                                    readonly=READ_ONLY)

@app.route("/dayview")
@cache.cached(timeout=7200, query_string=True)
def dayView():
    day   = int(flask.request.args.get("day"))
    month = int(flask.request.args.get("month"))
    year  = int(flask.request.args.get("year"))

    start  = datetime.datetime(year, month, day, tzinfo=pytz.utc)
    end    = start + oneDay - oneMillisecond

    prevDay = (start - oneDay)
    nextDay = (start + oneDay)

    hrefPrevDay   = dayLinkFormatString.format(prevDay.year, prevDay.month, prevDay.day)
    hrefNextDay   = dayLinkFormatString.format(nextDay.year, nextDay.month, nextDay.day)
    hrefThisMonth = monthLinkFormatString.format(start.year, start.month)

    dateOfViewString = start.strftime("%A, %d. %B %Y")

    events = backend.getEvents(start, end, db, backendparam)
    preparedTimeStrings = utils.parsing.prepareTimeStrings(events)

    return flask.render_template("day-view.html", events=events, \
                                    preparedTimeStrings=preparedTimeStrings, \
                                    prevDayLink=hrefPrevDay, \
                                    nextDayLink=hrefNextDay, \
                                    thisMonthLink=hrefThisMonth, \
                                    dateOfView=dateOfViewString,\
                                    readonly=READ_ONLY)

@app.route("/eventview")
@cache.cached(timeout=7200, query_string=True)
def eventView():
    eventID = flask.request.args.get("uid")
    event   = backend.getEventById(eventID, db, backendparam)
    if not event:
        return flask.Response("Event not found", status=404)

    dt = event.get("dtstart").dt
    backlinkDayView = dayLinkFormatString.format(dt.year, dt.month, dt.day)

    return flask.render_template("single-event-view.html", event=event,
                                    backlinkDayView=backlinkDayView, readonly=READ_ONLY)

@app.route("/eventedit", methods=["GET", "POST"])
def eventEdit():

    eventID = flask.request.args.get("uid")
    event   = None
    try:
        event = backend.getEventById(eventID, db, backendparam, noAmor=True)
    except KeyError:
        pass

    if not event:
        return flask.Response("Event not found.", status=404)

    if READ_ONLY:
        return "Editing disabled by command line option", 401

    if flask.request.method == "POST":
        params = flask.request.form
        event = utils.parsing.buildIcalEvent(params.get("title"), params.get("description"),
                                                params.get("location"), params.get("start-date"), 
                                                params.get("start-time"), params.get("end-date"), 
                                                params.get("end-time"), params.get("type"), inuid=eventID)

        editedEvent = backend.modifyEvent(eventID, event, backendparam)
        cache.clear()
        return flask.redirect("/eventview?uid={}&edited=true".format(eventID))
    else:
        startDate = event.get("dtstart").dt.strftime("%Y-%m-%d")
        startTime = event.get("dtstart").dt.strftime("%H:%M")
        endDate   = event.get("dtend").dt.strftime("%Y-%m-%d")
        endTime   = event.get("dtend").dt.strftime("%H:%M")

        return flask.render_template("eventedit.html", event=event, startDate=startDate,
                                        startTime=startTime, endDate=endDate, endTime=endTime)

#### API ####
@app.route("/upcoming")
def upcoming():
    startStr = flask.request.args.get("from")
    if startStr:
        start = datetime.datetime.fromtimestamp(int(startStr))
    else:
        start = datetime.datetime.utcnow()

    endStr = flask.request.args.get("to")
    if endStr:
        end = datetime.datetime.fromtimestamp(int(endStr))
    else:
        end = start + datetime.timedelta(days=60)

    start = start.replace(tzinfo=dateutil.tz.tzlocal())
    end   = end.replace(tzinfo=dateutil.tz.tzlocal())

    events = backend.getEvents(start, end, db, backendparam)
    return flask.render_template("partials/upcoming.html", events=events)

@app.route("/static/<path:path>")
def sendStatic(path):
    response = flask.send_from_directory('static', path)
    response.response.cache_control.max_age = 86400
    return response

@app.route("/service-worker.js")
def serviceWorker(): #must be served from root
    return app.send_static_file('service-worker.js')

@app.route("/invalidate-cache")
def invalidateCache():
    cache.clear()
    return "",204

@app.route("/static-cache-status")
def staticCacheStatus():
    return "",304

@app.route("/dynamic-cache-status")
def dynamicCacheStatus():
    return "",304
    
@app.route("/get-static-precache")
def staticCacheList():

    jsDir  = os.path.join(app.static_folder, 'js')
    jsFiles = ["/static/{}/{}".format("js", s) for s in os.listdir(jsDir)]
    jsFiles = list(filter(lambda x: "service-worker" not in x, jsFiles))
    
    cssDir = os.path.join(app.static_folder, 'css')
    cssFiles = ["/static/{}/{}".format("css", s) for s in os.listdir(cssDir)]
    
    data = json.dumps(jsFiles + cssFiles + ["/"])
    
    response = flask.Response(data, mimetype='application/json')
    response.headers["Cache-Control"] = "no-cache"
    return response

@app.route("/get-dynamic-precache")
def dynamicCacheList():
    
    #day   = int(flask.request.args.get("day"))
    if flask.request.args.get("server-decides"):
        month = datetime.datetime.today().month
        year  = datetime.datetime.today().year
    else:
        month = int(flask.request.args.get("month"))
        year  = int(flask.request.args.get("year"))
    
    start  = datetime.datetime(year, month, day=1, tzinfo=pytz.utc)
    end    = start + oneMonth - oneMillisecond

    prevMonth = start - oneMonth
    nextMonth = start + oneMonth
    
    # generate event links #
    events     = backend.getEvents(start, end, db, backendparam)
    eventLinks = [ "/eventview?uid=" + e["uid"] for e in events ]
    
    # generate day links #
    dayLinks = []
    for x in range(1, calendar.monthrange(year, month)[1] + 1):
        dayLinks += [ dayLinkFormatString.format(year, month, x) ]

    monthLinks = [ monthLinkFormatString.format(year, month) ]

    data = json.dumps(dayLinks + eventLinks + monthLinks)
    response = flask.Response(data, mimetype='application/json')
    response.headers["Cache-Control"] = "no-cache"
    return response
    

@app.route("/eventcreate", methods=["POST"])
def eventCreate():
    if READ_ONLY:
        return "Editing disabled by command line option", 401

    cache.clear()
    if flask.request.method == "POST":
        params = flask.request.form
        event = utils.parsing.buildIcalEvent(params.get("title"), params.get("description"),
                                                params.get("location"), params.get("start-date"), 
                                                params.get("start-time"), params.get("end-date"), 
                                                params.get("end-time"), params.get("type"))
        backend.createEvent(event, backendparam)

    response = flask.response("", status=204)
    response.headers["Cache-Control"] = "no-cache"
    return response

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calender webfront and gateway',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general parameters #
    parser.add_argument("-i", "--interface", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("-p", "--port", default="5000", help="Port to listen on")
    parser.add_argument("-b", "--backend", default="filesystem", help="fileystem|caldav|remoteics|hybrid")

    # localization #
    parser.add_argument("--locale-de", action='store_const', const=True, \
                            help="Use german localization for dates etc.")

    # backend specific parameters #
    parser.add_argument("--auth-file", default=None, \
                            help="Authentication file for backend (caldav/hybrid)")
    parser.add_argument("--remote-url", default=None, \
                            help="Remote url (caldav/hybrid)")
    parser.add_argument("--fs-backend-path", default="data", \
                            help="Path for locale directory (filesystem/hybrid)")
    parser.add_argument("--read-only", action="store_const", default=False, const=True, \
                            help="Disable editing the calendar (reply 401 in API and disable buttons)")

    args = parser.parse_args()
    READ_ONLY = args.read_only

    # set localization #
    if args.locale_de:
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")

    # read auth file #
    user, pw = (None, None)
    if args.auth_file:
        with open(args.auth_file) as f:
            user, pw =  f.read().strip("\n").split(",")

    #  set backend #
    if args.backend == "filesystem":
        backend = backends.filesystem
        backendparam = args.fs_backend_path
    elif args.backend == "remoteics":
        backend = backends.remoteICS
        if not args.read_only:
            READ_ONLY = True
            print("remoteICS does not support editing, setting readonly", file=sys.stderr)
        backendparam = args.remote_url
    elif args.backend == "caldav":
        backend = backends.remoteCaldav
        if not args.remote_url:
            raise ValueError("Missing Remote URL")
        backendparam = (args.remote_url, user, pw)
    elif args.backend == "hybrid":
        backend = backends.hybrid
        backendparam = (args.fs_backend_path, args.remote_url, user, pw)
    else:
        print("Unsupportet backend", file=sys.stderr)
        sys.exit(1)

    # startup #
    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)

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

backend = backends.filesystem
backendparam = None
READ_ONLY = False

app = flask.Flask("epic-open-calendar-frontend")
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
def eventView():
    eventID = flask.request.args.get("uid")
    event   = backend.getEventById(eventID, db, backendparam)

    if not event:
        return flask.Response("", status=404)

    dt = event.get("dtstart").dt
    backlinkDayView = dayLinkFormatString.format(dt.year, dt.month, dt.day)

    return flask.render_template("single-event-view.html", event=event,
                                    backlinkDayView=backlinkDayView, readonly=READ_ONLY)

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
    return flask.send_from_directory('static', path)


@app.route("/eventcreate", methods=["POST"])
def eventCreate():
    if READ_ONLY:
        return "Editing disabled by command line option", 401
    if flask.request.method == "POST":
        params = flask.request.form
        event = utils.parsing.buildIcalEvent(params.get("title"), params.get("description"),
                                                params.get("location"), params.get("start-date"), 
                                                params.get("start-time"), params.get("end-date"), 
                                                params.get("end-time"), params.get("type"))
        backend.createEvent(event, backendparam)
        db.update({event["uid"]:event})

    return "", 204

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calender webfront and gateway',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general parameters #
    parser.add_argument("-i", "--interface", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("-p", "--port", default="5000", help="Port to listen on")
    parser.add_argument("-b", "--backend", default="filesystem", help="Eithter filesystem, hybrid or caldav")

    # localization #
    parser.add_argument("--locale-de", action='store_const', const=True, \
                            help="Use german localization for dates etc.")

    # backend specific parameters #
    parser.add_argument("--auth-file", default=None, \
                            help="Authentication file for backend (caldav/hybrid(")
    parser.add_argument("--remote-url", default=None, \
                            help="Remote url (caldav/hybrid)")
    parser.add_argument("--fs-backend-path", default="data", \
                            help="Path for locale directory (filesystem/hybrid)")
    parser.add_argument("--read-only", action="store_const", default=False, const=True, \
                            help="Disable Editing the calendar (answer 401 at /eventcreat and disable buttons)")

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
    if args.backend == "remoteics":
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

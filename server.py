#!/usr/bin/python3

import flask

import sys
import argparse
import locale

import backends.filesystem
import utils.timeframe

import datetime
import dateutil.relativedelta
import dateutil.tz
import calendar
import pytz

backend = backends.filesystem
backendparam = "./data/"

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

    events              = backend.getEvents(start, end, db, backendparam)
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
                                        todayView=todayView)

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
                                    dateOfView=dateOfViewString)

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
                                    dateOfView=dateOfViewString)

@app.route("/eventview")
def eventView():
    eventID = flask.request.args.get("uid")
    event   = backend.getEventById(eventID, db, backendparam)

    if not event:
        return flask.Response("", status=404)

    dt = event.get("dtstart").dt
    backlinkDayView = dayLinkFormatString.format(dt.year, dt.month, dt.day)

    return flask.render_template("single-event-view.html", event=event,
                                    backlinkDayView=backlinkDayView)

#### API ####
@app.route("/upcoming")
def upcoming():
    start = datetime.datetime.fromtimestamp(flask.request.args.get("from"))
    end   = datetime.datetime.fromtimestamp(flask.request.args.get("to"))

    events = backend.getEvents(start, end, db, backendparam)
    preparedTimeStrings = utils.parsing.prepareTimeStrings(events)

    return flask.render_template("day-view.html", events=events, preparedTimeStrings=preparedTimeStrings)

@app.route("/static/<path:path>")
def sendStatic(path):
    return flask.send_from_directory('static', path)


@app.route("/eventcreate", methods=["POST"])
def eventCreate():
    if flask.request.method == "POST":
        params = flask.request.form
        print(params.get("end-time"))
        backend.createEvent(params.get("title"), params.get("description"),
                            params.get("location"), params.get("start-date"), params.get("start-time"),
                            params.get("end-date"), params.get("end-time"), params.get("type"))

    return "", 204

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start open-leaderboard',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general parameters #
    parser.add_argument("-i", "--interface", default="0.0.0.0",     help="Interface to listen on")
    parser.add_argument("-p", "--port",      default="5000",        help="Port to listen on")
    parser.add_argument("-b", "--backend",   default="filesystem",  help="Backend to use")

    # localization #
    parser.add_argument("--locale-de", action='store_const', const=True, \
                            help="Use german localization for dates etc.")

    # backend specific parameters #
    parser.add_argument("--auth-file", default="auth.token", \
                            help="Auth file for backend if nessesary")
    parser.add_argument("--remote-url", default=None, \
                            help="Remote url when using backend remote or google")
    parser.add_argument("--fs-backend-path", default="data", \
                            help="Path for locale file if backend 'filesystem' is used")
    parser.add_argument("--preheat", action='store_const', default=False, const=True, \
                            help="Preheat the backend")

    args = parser.parse_args()

    # set localization #
    if args.locale_de:
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")

    #  set backend #
    if args.backend == "filesystem":
        backend = backends.filesystem
        backendparam = args.fs_backend_path
    else:
        print("Unsupportet backend", file=sys.stderr)
        sys.exit(1)

    #  set backend variables #

    # backend preheat #
    if args.preheat:
        backend._parse(backendparam)

    # startup #
    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)

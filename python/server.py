import flask
import sys

import backends.filesystem
import utils.timeframe

backend = backends.filesystem

@app.route("/monthview")
def monthView():
    month = flask.request.get("month")
    year  = flask.request.get("year")

    events = backend.getEventTimestampsTupel()
    utils.timeframe.

    return flask.render_template()

@app.route("/dayview")
def dayView():
    day   = flask.request.get("day")
    month = flask.request.get("month")
    year  = flask.request.get("year")

    return flask.render_template()

@app.route("/eventview")
def eventView():
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
    
    #  set backend #
    if args.backend == "fileystem":
        backend = backends.fileystem
    else:
        print("Unsupportet backend", file=sys.stderr)
        sys.exit(1)

    #  set backend variables #


    # startup #
    args = parser.parse_args()
    app = flask.Flask("epic-open-calendar-frontend")
    app.run(interface=args.interface, port=args.port)

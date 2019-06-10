import flask

@app.route("/monthview")
def monthView():
    return  ""

@app.route("/dayview")
def dayView():
    return ""

@app.route("/eventview")
def eventView():
    return ""

@app.route("/static/<path:path>")
def sendStatic(path):
    return flask.send_from_directory('static', path)

if __name__ == "__main__":
    app = flask.Flask("epic-open-calendar-frontend")
    app.run()

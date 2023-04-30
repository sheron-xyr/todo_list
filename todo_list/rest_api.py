from flask import Flask, render_template, request, redirect, url_for
import flask
import sqlite3

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    db_filename = 'db.sqlite3'
    flask.g.sqlite_db = sqlite3.connect(str(db_filename))
    flask.g.sqlite_db.row_factory = dict_factory

    # Foreign keys have to be enabled per-connection.  This is an sqlite3
    # backwards compatibility thing.
    flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


def show_all_events():
    connection = get_db()
    cur = connection.execute(
        "SELECT * FROM eventtable "
        "ORDER BY deadline ASC, urgency DESC, eventname ASC"
    )
    result = cur.fetchall()
    connection.commit()
    return result

def add_one_event(name, days, urgency):
    connection = get_db()
    connection.execute(
        "INSERT INTO eventtable(eventname, deadline, urgency) "
        "VALUES (?, ?, ?)",
        (name, days, urgency)
    )
    connection.commit()
    new_event = {"eventname": name, "deadline": days, "urgency": urgency}
    return flask.jsonify(new_event)

def delete_one_event(name):
    connection = get_db()
    connection.execute(
        "DELETE FROM eventtable WHERE eventname=?",
        (name,)
    )
    connection.commit()
    return ''


app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/add')
def add():
    return render_template('addevent.html')

@app.route('/complete')
def complete():
    return render_template('delevent.html')

@app.route('/show')
def show():
    result = show_all_events()
    return render_template('result.html', result=result)

@app.route('/eventa', methods=["GET", "POST"])
def eventa():
    if request.method == "POST":
        name = request.form.get('event')
        days = request.form.get('days')
        urge = request.form.get('urgency')
        add_one_event(name, days, urge)
    return redirect(url_for('hello'))

@app.route('/eventd', methods=["GET", "POST"])
def eventd():
    if request.method == "POST":
        name = request.form.get('event')
        delete_one_event(name)
    return redirect(url_for('hello'))


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)

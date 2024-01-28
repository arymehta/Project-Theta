import os

import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///theta.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# main route
@app.route("/")
def index():
    if session.get("user_id"):
        return render_template(
            "index.html",
            name=db.execute(
                "SELECT username from users WHERE id = ?", session["user_id"]
            )[0]["username"],
        )
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    elif request.method == "GET":
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# makes a new account and saves it to database
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        if (
            not request.form.get("username")
            or not request.form.get("password")
            or not request.form.get("confirmation")
        ):
            return apology("Invalid", 400)  # if any field is missing

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords dont match", 400)

        else:
            record = db.execute(
                "SELECT id FROM users WHERE username = ?;", request.form.get("username")
            )
            if not record:  # if record does not already exist
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (? , ?);",
                    request.form.get("username"),
                    generate_password_hash(request.form.get("password")),
                )
                rows = db.execute(
                    "SELECT * FROM users WHERE username = ?",
                    request.form.get("username"),
                )
                session["user_id"] = rows[0]["id"]

                return redirect("/")
            else:
                return apology("Username already taken")


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "GET":
        return render_template("changepass.html")
    elif request.method == "POST":
        if not request.form.get("newpass") or not request.form.get(
            "confirmation"
        ):  # any field empty
            return apology("Invalid")

        elif request.form.get("newpass") != request.form.get(
            "confirmation"
        ):  # do not match
            return apology("Passwords Dont Match!")

        else:
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?",
                generate_password_hash(request.form.get("newpass")),
                session["user_id"],
            )
            return redirect("/")


@app.route("/timer", methods=["POST", "GET"])
@login_required
def timer():
    if request.method == "GET":
        # display table of studytimes
        return render_template(
            "clock.html",
            entries=db.execute(
                "SELECT * FROM studytimes WHERE usr_id = ? ORDER BY date DESC LIMIT 10;",
                session["user_id"],
            ),
        )
    elif request.method == "POST":
        data = request.json
        hours = data["hours"]
        minutes = data["minutes"]
        seconds = data["seconds"]

        if hours or minutes or seconds:
            # adds a new entry to table
            db.execute(
                "INSERT INTO studytimes (usr_id, hours, minutes, seconds, date) VALUES (?, ?, ?, ?, ?)",
                session["user_id"],
                hours,
                minutes,
                seconds,
                datetime.now(),
            )
    return redirect("/timer")


@app.route("/todo", methods=["POST", "GET"])
@login_required
def todo():
    if request.method == "POST":
        # gets existing todo items
        db.execute(
            "INSERT INTO todo (usr_id, todo_item, status, date) VALUES (?, ?, ?, ?);",
            session["user_id"],
            request.form.get("newtodo"),
            "NOT DONE",
            datetime.now(),
        )
        return redirect("/todo")

    elif request.method == "GET":
        todolist = db.execute(
            "SELECT * FROM todo WHERE usr_id = ? ORDER BY id DESC;", session["user_id"]
        )
        return render_template("todo.html", todolist=todolist)


@app.route("/deleteTODO", methods=["POST"])
@login_required
def deleteTODO():
    if request.form.get("delete"):
        db.execute("DELETE FROM todo WHERE id = ?", request.form.get("delete"))
        return redirect("/todo")

    elif request.form.get("cancel"):
        # strikes text inside a todo
        status = db.execute(
            "SELECT status FROM todo WHERE id = ?", request.form.get("cancel")
        )[0]["status"]
        if status == "NOT DONE":
            db.execute(
                "UPDATE todo SET status = ? WHERE id = ?",
                "DONE",
                request.form.get("cancel"),
            )
        if status == "DONE":
            db.execute(
                "UPDATE todo SET status = ? WHERE id = ?",
                "NOT DONE",
                request.form.get("cancel"),
            )
        return redirect("/todo")


@app.route("/notes", methods=["POST", "GET"])
@login_required
def notes():
    if request.method == "POST":
        db.execute(
            "INSERT INTO note (usr_id, note, date) VALUES (?, ?, ?);",
            session["user_id"],
            request.form.get("newnote"),
            datetime.now(),
        )
        return redirect("/notes")

    elif request.method == "GET":
        return render_template(
            "notes.html",
            notes=db.execute(
                "SELECT * FROM note WHERE usr_id = ? ORDER BY id DESC;",
                session["user_id"],
            ),
        )


@app.route("/deleteNOTE", methods=["POST"])
@login_required
def deleteNOTE():
    if request.form.get("delete"):
        # removes a note from the DB
        db.execute("DELETE FROM note WHERE id = ?", request.form.get("id"))
    return redirect("/notes")


# displays html file with youtube video player embed
@app.route("/music")
@login_required
def music():
    return render_template("music.html")


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"

DATABASE = "db.sqlite"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript(open("db_setup.sql").read())

@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with get_db() as db:
            db.execute("INSERT INTO users (username, password, euro, bitcoin, is_admin) VALUES (?, ?, 100, 0, 0)",
                       (username, password))
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            if user:
                session["user_id"] = user["id"]
                session["is_admin"] = bool(user["is_admin"])
                return redirect("/dashboard")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        price = db.execute("SELECT price FROM bitcoin_price ORDER BY time DESC LIMIT 1").fetchone()
    return render_template("dashboard.html", user=user, price=price["price"])

@app.route("/buy", methods=["POST"])
def buy():
    if "user_id" not in session:
        return redirect("/login")
    amount = float(request.form["amount"])
    with get_db() as db:
        price = db.execute("SELECT price FROM bitcoin_price ORDER BY time DESC LIMIT 1").fetchone()["price"]
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        cost = price * amount
        if user["euro"] >= cost:
            db.execute("UPDATE users SET euro = euro - ?, bitcoin = bitcoin + ? WHERE id = ?",
                       (cost, amount, session["user_id"]))
    return redirect("/dashboard")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user_id" not in session or not session.get("is_admin"):
        return redirect("/login")
    message = ""
    if request.method == "POST":
        if "admin_code" in request.form and request.form["admin_code"] == "Frog20095615":
            session["is_admin"] = True
        elif "new_price" in request.form:
            price = float(request.form["new_price"])
            with get_db() as db:
                db.execute("INSERT INTO bitcoin_price (price, time) VALUES (?, ?)",
                           (price, datetime.now()))
            message = "Курс обновлён."
        elif "give_euro" in request.form:
            uid = int(request.form["user_id"])
            amount = float(request.form["euro_amount"])
            with get_db() as db:
                db.execute("UPDATE users SET euro = euro + ? WHERE id = ?", (amount, uid))
            message = "Евро выданы."
    with get_db() as db:
        users = db.execute("SELECT * FROM users").fetchall()
        history = db.execute("SELECT * FROM bitcoin_price ORDER BY time DESC LIMIT 20").fetchall()
    return render_template("admin.html", users=users, history=history, message=message)

@app.route("/price-history")
def price_history():
    with get_db() as db:
        data = db.execute("SELECT * FROM bitcoin_price ORDER BY time").fetchall()
        return jsonify([{"time": row["time"], "price": row["price"]} for row in data])

if __name__ == "__main__":
    app.run(debug=True)

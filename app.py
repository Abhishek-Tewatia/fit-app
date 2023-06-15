from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = 'jfhajkkkfjajkdf'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db = SQL("sqlite:///database/user_info.db")
db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
    );""")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.execute("SELECT * FROM users WHERE email= :email", email=email)
        if user and user[0]['password'] == password:
            session['user_id'] = user[0]['id']
            return redirect('/profile')
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    else:
        return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        try:
            db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)", username=username, password=password, email=email)
            return redirect('/login')
            db.commit()
        except:
            error = 'Username already exists'
            return render_template('signup.html', error=error)
    else:
        return render_template("signup.html")

@app.route("/workouts")
def workplan():
    return render_template("workplan.html")

@app.route("/community")
def community():
    return render_template("community.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/getstarted")

@app.route("/getstarted")
def getstarted():
    return render_template("getstarted.html")

@app.route("/workouts/Weight-Gain")
def wg():
    return render_template("wg.html")

@app.route("/workouts/Weight-Loss")
def wl():
    return render_template("wl.html")

@app.route("/workouts/Daily-Fitness")
def df():
    return render_template("df.html")

@app.route("/workouts/Bodybuilding")
def bb():
    return render_template("bb.html")

# @app.route("/nutrition")
# def nutrition():
#     return render_template("nutrition.html")

db1 = SQL("sqlite:///database/user_stats.db")
db1.execute("""CREATE TABLE IF NOT EXISTS stats (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT NOT NULL,
                  weight FLOAT NOT NULL DEFAULT 0,
                  height FLOAT NOT NULL DEFAULT 0,
                  bmi FLOAT NOT NULL DEFAULT 0,
                  calorie_intake FLOAT NOT NULL DEFAULT 0
              );""")

db1.execute("""CREATE TABLE IF NOT EXISTS tracker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT NOT NULL,
                    calorie_intake FLOAT NOT NULL,
                    water_intake FLOAT NOT NULL,
                    email TEXT NOT NULL,
                    FOREIGN KEY (email) REFERENCES users (email)
              );""")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    conn = sqlite3.connect('database/user_stats.db')
    c = conn.cursor()
    user_id = session.get('user_id', None)
    if user_id is None:
        return redirect("/login")
    else:
        user = db.execute("SELECT email FROM users WHERE id = :id", id=user_id)
        email = user[0]["email"]
        
        result = c.execute("SELECT id FROM stats WHERE email = ?", (email,))
        if result.fetchone() is None:
            db1.execute("INSERT INTO stats (email) VALUES (?)", (email,))

    c.execute("SELECT weight, height, calorie_intake FROM stats WHERE email=?", (email,))
    user_details = c.fetchone()

    if request.method == "POST":
        weight = request.form.get("weight")
        height = request.form.get("height")
        db1.execute("UPDATE stats SET weight=?, height=? WHERE email=?", (weight, height, email))
        db1.commit()

    weight = user_details[0]
    height = user_details[1]
    
    if weight and height:
        weight = float(weight)
        height = float(height)
        bmi = round(weight / height**2, 1)    
    else:
        bmi = None

    c.execute("SELECT day, calorie_intake, water_intake FROM tracker WHERE email=?", (email,))
    tracker_entries = c.fetchall()
    
    conn.close()
    
    return render_template("profile.html", weight=weight, height=height, bmi=bmi, tracker_entries=tracker_entries)

@app.route('/add_tracker_entry', methods=['POST'])
def add_tracker_entry():
    if request.method == 'POST':
        date = datetime.date.today().strftime('%Y-%m-%d')
        water_intake = request.form.get('water_intake')
        calorie_intake = request.form.get('calorie_intake')
        user_id = session.get('user_id', None)
        if user_id is None:
            return redirect("/login")
        user = db.execute("SELECT email FROM users WHERE id = :id", id=user_id)
        email = user[0]["email"]

        conn = sqlite3.connect('database/user_stats.db')
        c = conn.cursor()

        result = c.execute("SELECT day FROM tracker WHERE day = ? AND email = ?", (date, email))
        existing_date = result.fetchone()

        if existing_date:
            c.execute("UPDATE tracker SET water_intake = water_intake + ?, calorie_intake = calorie_intake + ? WHERE day = ? AND email = ?",
                      (water_intake, calorie_intake, date, email))
        else:
            c.execute("INSERT INTO tracker (day, water_intake, calorie_intake, email) VALUES (?, ?, ?, ?)",
                      (date, water_intake, calorie_intake, email))

        conn.commit()
        conn.close()

    return redirect('/profile')


@app.route('/modify_height', methods=['POST'])
def modify_height():
    user_id = session.get('user_id', None)
    if user_id is None:
        return redirect("/login")
    new_height = request.form['height']
    conn = sqlite3.connect('database/user_stats.db')
    c = conn.cursor()
    c.execute("UPDATE stats SET height=? WHERE id=?", (new_height, user_id))
    conn.commit()
    conn.close()
    return redirect("profile")

@app.route('/modify_weight', methods=['POST'])
def modify_weight():
    user_id = session.get('user_id', None)
    if user_id is None:
        return redirect("/login")
    new_weight = request.form['weight']
    conn = sqlite3.connect('database/user_stats.db')
    c = conn.cursor()
    c.execute("UPDATE stats SET weight=? WHERE id=?", (new_weight, user_id))
    conn.commit()
    conn.close()
    return redirect("profile")


DATABASE = 'database/food_data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/nutrition', methods=['GET', 'POST'])
def nutrition():
    query = request.form.get('food')
    results = []
    food = None

    if query:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data WHERE food_name LIKE ?", ('%' + query + '%',))
        results = cursor.fetchall()
        conn.close()

    if request.method == 'POST':
        if results:
            return render_template('nutrition.html', query=query, results=results)
        else:
            return render_template('nutrition.html', query=query)

    return render_template('nutrition.html', food=food)


db2 = SQL("sqlite:///database/food_data.db")

@app.route("/food/<code>")
def food_details(code):
    food = db2.execute("SELECT * FROM data WHERE code = :code", code=code)
    if food:
        return render_template("nutrition.html", food=food[0])
    else:
        return "Food not found"




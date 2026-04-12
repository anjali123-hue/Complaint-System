from flask import Flask, render_template, request, redirect
import mysql.connector
import os

app = Flask(__name__)

# ✅ FIXED DB CONNECTION (Railway Public)
def get_db():
    return mysql.connector.connect(
        host="caboose.proxy.rlwy.net",
        user="root",
        password="uMIHnXwWNSuNEnDVRwYgXLHsuopzIbqp",
        database="railway",
        port=53743
    )

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM complaints ORDER BY date DESC")
    complaints = cursor.fetchall()

    return render_template("index.html", complaints=complaints)

@app.route('/add', methods=['POST'])
def add():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO complaints (name, email, message, status, date) VALUES (%s,%s,%s,%s,NOW())",
        (request.form['name'], request.form['email'], request.form['message'], "Pending")
    )

    db.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM complaints WHERE id=%s", (id,))
    db.commit()

    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM complaints WHERE id=%s", (id,))
    c = cursor.fetchone()

    return render_template("edit.html", c=c)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE complaints SET status=%s WHERE id=%s",
        (request.form['status'], id)
    )

    db.commit()
    return redirect('/')

# ✅ IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
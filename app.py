from flask import Flask, render_template, request, redirect, Response
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="caboose.proxy.rlwy.net",
        user="root",
        password="uMIHnXwWNSuNEnDVRwYgXLHsuopzIbqp",
        database="railway",
        port=53743
    )

@app.route('/')
def landing():
    return render_template("landing.html")

@app.route('/user')
def user():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints ORDER BY date DESC")
    complaints = cursor.fetchall()
    db.close()
    return render_template("user.html", complaints=complaints)

@app.route('/add', methods=['POST'])
def add():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO complaints (name, email, category, message, status, priority, date) VALUES (%s,%s,%s,%s,%s,%s,NOW())",
        (
            request.form['name'],
            request.form['email'],
            request.form['category'],
            request.form['message'],
            "Pending",
            request.form['priority']
        )
    )

    db.commit()
    db.close()
    return redirect('/user')

@app.route('/admin')
def admin():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints ORDER BY date DESC")
    complaints = cursor.fetchall()
    db.close()

    for c in complaints:
        try:
            if c['resolved_date']:
                c['time_taken'] = (c['resolved_date'] - c['date']).days
            else:
                c['time_taken'] = (datetime.now() - c['date']).days
        except:
            c['time_taken'] = 0

    return render_template("admin.html", complaints=complaints)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    db = get_db()
    cursor = db.cursor()

    status = request.form['status']

    if status == "Resolved":
        cursor.execute(
            "UPDATE complaints SET status=%s, resolved_date=NOW() WHERE id=%s",
            (status, id)
        )
    else:
        cursor.execute(
            "UPDATE complaints SET status=%s WHERE id=%s",
            (status, id)
        )

    db.commit()
    db.close()
    return redirect('/admin')

@app.route('/download_report')
def download_report():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, email, category, message, status, priority, date FROM complaints")
    data = cursor.fetchall()
    db.close()

    csv = "Name, Email, Category, Message, Status, Priority, Date\n"
    for row in data:
        csv += f"{row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}\n"

    return Response(
        csv,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=report.csv"}
    )

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM complaints WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect('/admin')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
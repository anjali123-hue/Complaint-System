from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
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
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints ORDER BY date DESC")
    complaints = cursor.fetchall()
    return render_template("user.html", complaints=complaints)

@app.route('/add', methods=['POST'])
def add():
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
    return redirect('/user')

@app.route('/admin')
def admin():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints ORDER BY date DESC")
    complaints = cursor.fetchall()

    # CALCULATE TIME TAKEN
    for c in complaints:
        if c['resolved_date']:
            c['time_taken'] = (c['resolved_date'] - c['date']).days
        else:
            c['time_taken'] = (datetime.now() - c['date']).days

    return render_template("admin.html", complaints=complaints)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    status = request.form['status']
    cursor = db.cursor()

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
    return redirect('/admin')

@app.route('/download_report')
def download_report():
    cursor = db.cursor()
    cursor.execute("SELECT name, category, priority, status, date FROM complaints")
    data = cursor.fetchall()

    csv = "Name, Category, Priority, Status, Date\n"
    for row in data:
        csv += f"{row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}\n"

    return app.response_class(
        csv,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=report.csv"}
    )

@app.route('/delete/<int:id>')
def delete(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM complaints WHERE id=%s", (id,))
    db.commit()
    return redirect('/admin')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
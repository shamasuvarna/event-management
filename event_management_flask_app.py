from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

# ----------------- MYSQL DATABASE CONNECTION -----------------
db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", "Shama@2005"),
    database=os.getenv("DB_NAME", "event_management"),
    auth_plugin='mysql_native_password'
)
cursor = db.cursor(dictionary=True)
# --------------------------------------------------------------


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('home.html')


# ============================================================
#                    ORGANIZERS CRUD
# ============================================================

# LIST ORGANIZERS
@app.route('/organizers')
def organizers():
    cursor.execute("SELECT * FROM organizers ORDER BY organizer_id DESC")
    organizers = cursor.fetchall()
    return render_template('organizers.html', organizers=organizers)


# ADD ORGANIZER
@app.route('/add_organizer', methods=['GET', 'POST'])
def add_organizer():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()

        cursor.execute("""
            INSERT INTO organizers (name, email, phone)
            VALUES (%s, %s, %s)
        """, (name, email, phone))
        db.commit()
        return redirect('/organizers')

    return render_template('add_organizer.html')


# EDIT ORGANIZER
@app.route('/edit_organizer/<int:id>', methods=['GET', 'POST'])
def edit_organizer(id):
    cursor.execute("SELECT * FROM organizers WHERE organizer_id=%s", (id,))
    organizer = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cursor.execute("""
            UPDATE organizers
            SET name=%s, email=%s, phone=%s
            WHERE organizer_id=%s
        """, (name, email, phone, id))
        db.commit()
        return redirect('/organizers')

    return render_template('edit_organizer.html', organizer=organizer)


# DELETE ORGANIZER
@app.route('/delete_organizer/<int:id>')
def delete_organizer(id):
    cursor.execute("DELETE FROM organizers WHERE organizer_id=%s", (id,))
    db.commit()
    return redirect('/organizers')


# ============================================================
#                    EVENTS CRUD
# ============================================================

@app.route('/events')
def events():
    cursor.execute("""
        SELECT e.*, o.name AS organizer_name 
        FROM events e 
        LEFT JOIN organizers o ON e.organizer_id = o.organizer_id
        ORDER BY e.event_id DESC
    """)
    events = cursor.fetchall()
    return render_template('events.html', events=events)


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    cursor.execute("SELECT * FROM organizers")
    organizers = cursor.fetchall()

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        venue = request.form['venue']
        organizer_id = request.form['organizer_id']
        description = request.form['description']

        cursor.execute("""
            INSERT INTO events (event_name, event_date, venue, organizer_id, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (event_name, event_date, venue, organizer_id, description))
        db.commit()
        return redirect('/events')

    return render_template('add_event.html', organizers=organizers)


@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    cursor.execute("SELECT * FROM events WHERE event_id=%s", (id,))
    event = cursor.fetchone()
    cursor.execute("SELECT * FROM organizers")
    organizers = cursor.fetchall()

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        venue = request.form['venue']
        organizer_id = request.form['organizer_id']
        description = request.form['description']

        cursor.execute("""
            UPDATE events SET event_name=%s, event_date=%s, venue=%s,
            organizer_id=%s, description=%s
            WHERE event_id=%s
        """, (event_name, event_date, venue, organizer_id, description, id))
        db.commit()
        return redirect('/events')

    return render_template('edit_event.html', event=event, organizers=organizers)


@app.route('/delete_event/<int:id>')
def delete_event(id):
    cursor.execute("DELETE FROM events WHERE event_id=%s", (id,))
    db.commit()
    return redirect('/events')


# ============================================================
#                    PARTICIPANTS CRUD
# ============================================================

@app.route('/participants')
def participants():
    cursor.execute("SELECT * FROM participants ORDER BY participant_id DESC")
    participants = cursor.fetchall()
    return render_template('participants.html', participants=participants)


@app.route('/add_participant', methods=['GET', 'POST'])
def add_participant():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cursor.execute("""
            INSERT INTO participants (name, email, phone)
            VALUES (%s, %s, %s)
        """, (name, email, phone))
        db.commit()
        return redirect('/participants')

    return render_template('add_participant.html')


@app.route('/edit_participant/<int:id>', methods=['GET', 'POST'])
def edit_participant(id):
    cursor.execute("SELECT * FROM participants WHERE participant_id=%s", (id,))
    participant = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cursor.execute("""
            UPDATE participants
            SET name=%s, email=%s, phone=%s
            WHERE participant_id=%s
        """, (name, email, phone, id))
        db.commit()
        return redirect('/participants')

    return render_template('edit_participant.html', participant=participant)


@app.route('/delete_participant/<int:id>')
def delete_participant(id):
    cursor.execute("DELETE FROM participants WHERE participant_id=%s", (id,))
    db.commit()
    return redirect('/participants')


# ============================================================
#                    REGISTRATIONS CRUD
# ============================================================

@app.route('/registrations')
def registrations():
    cursor.execute("""
        SELECT r.*, e.event_name, p.name AS participant_name
        FROM registrations r
        LEFT JOIN events e ON r.event_id = e.event_id
        LEFT JOIN participants p ON r.participant_id = p.participant_id
        ORDER BY r.registration_id DESC
    """)
    registrations = cursor.fetchall()
    return render_template('registrations.html', registrations=registrations)


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.execute("SELECT * FROM participants")
    participants = cursor.fetchall()

    if request.method == 'POST':
        event_id = request.form['event_id']
        participant_id = request.form['participant_id']
        reg_date = datetime.now()

        cursor.execute("""
            INSERT INTO registrations (event_id, participant_id, registration_date)
            VALUES (%s, %s, %s)
        """, (event_id, participant_id, reg_date))
        db.commit()
        return redirect('/registrations')

    return render_template('register.html', events=events, participants=participants)


@app.route('/edit_registration/<int:id>', methods=['GET', 'POST'])
def edit_registration(id):
    cursor.execute("SELECT * FROM registrations WHERE registration_id=%s", (id,))
    reg = cursor.fetchone()

    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.execute("SELECT * FROM participants")
    participants = cursor.fetchall()

    if request.method == 'POST':
        event_id = request.form['event_id']
        participant_id = request.form['participant_id']

        cursor.execute("""
            UPDATE registrations
            SET event_id=%s, participant_id=%s
            WHERE registration_id=%s
        """, (event_id, participant_id, id))
        db.commit()
        return redirect('/registrations')

    return render_template('edit_registration.html', reg=reg, events=events, participants=participants)


@app.route('/delete_registration/<int:id>')
def delete_registration(id):
    cursor.execute("DELETE FROM registrations WHERE registration_id=%s", (id,))
    db.commit()
    return redirect('/registrations')


# --------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql123*'
app.config['MYSQL_DB'] = 'bus_booking'

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('search'))
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # ✅ FIXED
        cursor.execute("SELECT * FROM buses WHERE source = %s AND destination = %s", (source, destination))
        buses = cursor.fetchall()
        cursor.close()

        return render_template('search_results.html', buses=buses)

    return render_template('search.html')
@app.route('/book/<int:bus_id>', methods=['POST'])
def book(bus_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # ✅ Use DictCursor
    
    # Get number of seats from form
    num_seats = int(request.form.get("num_seats", 0))
    if num_seats <= 0:
        return "Invalid number of seats", 400  # Handle incorrect inputs

    # Fetch available seats from database
    cursor.execute("SELECT available_seats FROM buses WHERE id = %s", (bus_id,))
    bus = cursor.fetchone()

    if not bus or num_seats > bus["available_seats"]:  # ✅ Access as dictionary
        return "Not enough seats available", 400  # Handle overbooking

    # Store passenger details
    passengers = []
    for i in range(1, num_seats + 1):
        passenger_name = request.form.get(f'passenger_name_{i}')
        passenger_age = request.form.get(f'passenger_age_{i}')
        
        if not passenger_name or not passenger_age:
            return "Missing passenger details", 400  # Ensure all fields are filled

        passengers.append((bus_id, passenger_name, int(passenger_age)))

    # Insert passengers into `bookings` table
    cursor.executemany(
        "INSERT INTO bookings (bus_id, passenger_name, passenger_age) VALUES (%s, %s, %s)",
        passengers
    )

    # Update available seats
    cursor.execute(
        "UPDATE buses SET available_seats = available_seats - %s WHERE id = %s",
        (num_seats, bus_id)
    )
    mysql.connection.commit()
    cursor.close()

    return '''
    <h2>Booked Successfully!</h2>
    <form action="/logout" method="GET">
        <button type="submit">Logout</button>
    </form>
'''
 # You can modify this to redirect

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

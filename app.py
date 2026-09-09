from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "mounika_secret"

# Connect DB
def get_db():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table with all new columns
def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        genre TEXT,
        year INTEGER,
        rating INTEGER,
        mood TEXT DEFAULT 'Happy 😊',
        rewatch_count INTEGER DEFAULT 1
    )''')
    conn.commit()
    # For old DB - add new columns safely
    try:
        conn.execute("ALTER TABLE movies ADD COLUMN mood TEXT DEFAULT 'Happy 😊'")
    except: pass
    try:
        conn.execute("ALTER TABLE movies ADD COLUMN rewatch_count INTEGER DEFAULT 1")
    except: pass

init_db()

@app.route('/')
def index():
    conn = get_db()
    movies = conn.execute("SELECT * FROM movies ORDER BY id DESC").fetchall()
    return render_template('index.html', movies=movies)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name'].strip()
    genre = request.form['genre']
    year = request.form['year']
    rating = request.form['rating']
    mood = request.form['mood']  # NEW for Feature 3

    conn = get_db()

    # Duplicate Blocker (your old feature)
    existing = conn.execute("SELECT * FROM movies WHERE LOWER(name)=LOWER(?)", (name,)).fetchone()
    if existing:
        flash(f"⚠️ '{name}' already exists! You added it before!")
        return redirect('/')

    conn.execute("INSERT INTO movies (name, genre, year, rating, mood, rewatch_count) VALUES (?,?,?,?,?,1)",
                 (name, genre, year, rating, mood))
    conn.commit()
    flash(f"✅ '{name}' added!")
    return redirect('/')

# NEW for Feature 1 - Rewatch Counter
@app.route('/rewatch/<int:id>')
def rewatch(id):
    conn = get_db()
    conn.execute("UPDATE movies SET rewatch_count = rewatch_count + 1 WHERE id=?", (id,))
    conn.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM movies WHERE id=?", (id,))
    conn.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
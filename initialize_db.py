import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create clubs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Create students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            club_id INTEGER,
            paid INTEGER NOT NULL DEFAULT 0,
            last_payment_date TEXT,
            next_payment_date TEXT,
            FOREIGN KEY(club_id) REFERENCES clubs(id)
        )
    ''')

    # Clear existing data
    c.execute('DELETE FROM clubs')
    c.execute('DELETE FROM students')

    # Insert test data
    c.execute('INSERT INTO clubs (name) VALUES ("باشگاه هلال احمر")')
    c.execute('INSERT INTO clubs (name) VALUES ("باشگاه امام علی")')

    # Use Gregorian dates for simplicity in this example
    c.execute('INSERT INTO students (name, club_id, paid, last_payment_date, next_payment_date) VALUES (?, ?, ?, ?, ?)',
              ('علی', 1, 0, '', '2024-08-22'))
    c.execute('INSERT INTO students (name, club_id, paid, last_payment_date, next_payment_date) VALUES (?, ?, ?, ?, ?)',
              ('محمد', 1, 1, '2024-07-15', '2024-08-22'))
    c.execute('INSERT INTO students (name, club_id, paid, last_payment_date, next_payment_date) VALUES (?, ?, ?, ?, ?)',
              ('سارا', 2, 0, '', '2024-08-22'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()

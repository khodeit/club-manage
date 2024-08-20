import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('SELECT * FROM clubs')
clubs = c.fetchall()
print('Clubs:', clubs)

c.execute('SELECT * FROM students')
students = c.fetchall()
print('Students:', students)

conn.close()

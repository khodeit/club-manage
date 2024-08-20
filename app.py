from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import jdatetime

app = Flask(__name__)

def convert_to_jalali(date):
    return jdatetime.date.fromgregorian(date=date).strftime('%Y/%m/%d')

def convert_to_gregorian(jalali_date):
    if not jalali_date:
        return ''
    year, month, day = map(int, jalali_date.split('/'))
    return jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clubs')
def clubs():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM clubs')
    clubs_list = c.fetchall()
    conn.close()
    return jsonify([{'id': club[0], 'name': club[1]} for club in clubs_list])

@app.route('/students')
def students():
    club_id = request.args.get('club_id', type=int)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    today = datetime.now().date()
    c.execute('''
        SELECT id, name, paid, last_payment_date, next_payment_date FROM students WHERE club_id = ?
    ''', (club_id,))
    students = c.fetchall()
    conn.close()

    total_students = 0
    paid_students = 0
    unpaid_students = 0

    result = []
    for student in students:
        student_id, name, paid, last_payment_date, next_payment_date = student

        # Update statistics
        total_students += 1
        if paid == 1:
            paid_students += 1
        else:
            unpaid_students += 1

        # Convert dates
        try:
            if last_payment_date:
                last_payment_date = convert_to_jalali(datetime.strptime(last_payment_date, '%Y-%m-%d').date())
            if next_payment_date:
                next_payment_date = convert_to_jalali(datetime.strptime(next_payment_date, '%Y-%m-%d').date())
        except ValueError as e:
            print(f"Error converting date: {e}")
            last_payment_date = ''
            next_payment_date = ''

        # Sorting and adding to the result list
        if paid == 1 and next_payment_date:
            result.append({
                'id': student_id,
                'name': name,
                'paid': paid,
                'last_payment_date': last_payment_date,
                'next_payment_date': next_payment_date
            })
        elif paid == 0 and (not last_payment_date or today > datetime.strptime(convert_to_gregorian(next_payment_date), '%Y-%m-%d').date()):
            result.insert(0, {
                'id': student_id,
                'name': name,
                'paid': paid,
                'last_payment_date': last_payment_date,
                'next_payment_date': next_payment_date
            })
        else:
            result.append({
                'id': student_id,
                'name': name,
                'paid': paid,
                'last_payment_date': last_payment_date,
                'next_payment_date': next_payment_date
            })

    return jsonify({
        'students': result,
        'total': total_students,
        'paid': paid_students,
        'unpaid': unpaid_students
    })

@app.route('/update_status', methods=['POST'])
def update_status():
    student_id = request.json.get('id')
    paid = request.json.get('paid')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    today = datetime.now().date()
    if paid:
        last_payment_date = today
        next_payment_date = today + timedelta(days=30)
        c.execute('UPDATE students SET paid = ?, last_payment_date = ?, next_payment_date = ? WHERE id = ?',
                  (paid, last_payment_date.strftime('%Y-%m-%d'), next_payment_date.strftime('%Y-%m-%d'), student_id))
    else:
        c.execute('UPDATE students SET paid = ?, last_payment_date = ?, next_payment_date = ? WHERE id = ?',
                  (paid, '', '', student_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    name = data.get('name')
    club_id = data.get('club_id')

    if name and club_id:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO students (name, club_id, paid, last_payment_date, next_payment_date) VALUES (?, ?, ?, ?, ?)',
                  (name, club_id, 0, '', ''))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400


if __name__ == '__main__':
    app.run(debug=True)

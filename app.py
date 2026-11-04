import pymysql
import pymysql.cursors
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from datetime import date, timedelta

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    # Connects using PyMySQL with parameters defined in config.py
    # Fallbacks are provided, but ideally pulled from os.environ
    conn = pymysql.connect(
        host=app.config.get('MYSQL_HOST', 'localhost'),
        user=app.config.get('MYSQL_USER', 'admin'),
        password=app.config.get('MYSQL_PASSWORD', ''),
        database=app.config.get('MYSQL_DB', 'library'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

# ---------------------------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            
            # Route based on role
            if user['role'] == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------------------------------------------------------------
# Staff Routes (Manage Inventory & Users)
# ---------------------------------------------------------------------------
@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM books ORDER BY added_on DESC LIMIT 5')
        books = cursor.fetchall()
    conn.close()
    
    return render_template('staff_dashboard.html', books=books)

# ---------------------------------------------------------------------------
# Student Routes (View Rented Books)
# ---------------------------------------------------------------------------
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('''
            SELECT books.title, books.author, borrowings.issue_date, borrowings.due_date, borrowings.status 
            FROM borrowings 
            JOIN books ON borrowings.book_id = books.id 
            WHERE borrowings.user_id = %s
        ''', (session['user_id'],))
        my_books = cursor.fetchall()
    conn.close()
    
    return render_template('student_dashboard.html', my_books=my_books)

# ---------------------------------------------------------------------------
# Staff Routes (Manage Inventory)
# ---------------------------------------------------------------------------
@app.route('/staff/books')
def manage_books():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM books ORDER BY id DESC')
        books = cursor.fetchall()
    conn.close()
    
    return render_template('books.html', books=books)

@app.route('/staff/books/add', methods=['POST'])
def add_book():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    title = request.form['title']
    author = request.form['author']
    isbn = request.form['isbn']
    copies = int(request.form['copies'])
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES (%s, %s, %s, %s, %s)',
                           (title, author, isbn, copies, copies))
        conn.commit()
        flash(f'"{title}" added successfully!', 'success')
    except pymysql.err.IntegrityError:
        flash('A book with this ISBN already exists in the catalog.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('manage_books'))

@app.route('/staff/books/edit/<int:id>', methods=['POST'])
def edit_book(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    title = request.form['title']
    author = request.form['author']
    isbn = request.form['isbn']
    new_total = int(request.form['copies'])
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT total_copies, available_copies FROM books WHERE id = %s', (id,))
        old_book = cursor.fetchone()
        
        if old_book:
            delta = new_total - old_book['total_copies']
            new_available = old_book['available_copies'] + delta
            
            if new_available < 0:
                flash('Cannot reduce total copies below the amount currently issued to students.', 'danger')
            else:
                try:
                    cursor.execute('''
                        UPDATE books 
                        SET title = %s, author = %s, isbn = %s, total_copies = %s, available_copies = %s 
                        WHERE id = %s
                    ''', (title, author, isbn, new_total, new_available, id))
                    conn.commit()
                    flash('Book updated successfully!', 'success')
                except pymysql.err.IntegrityError:
                    flash('ISBN already in use by another book.', 'danger')
                    
    conn.close()
    return redirect(url_for('manage_books'))

@app.route('/staff/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Use an alias 'count' so we can fetch it via DictCursor
        cursor.execute('SELECT count(*) as count FROM borrowings WHERE book_id = %s AND status = "Issued"', (id,))
        active_borrows = cursor.fetchone()['count']
        
        if active_borrows > 0:
            flash('Cannot delete book. Copies are currently issued to users.', 'danger')
        else:
            cursor.execute('DELETE FROM books WHERE id = %s', (id,))
            cursor.execute('DELETE FROM borrowings WHERE book_id = %s', (id,))
            conn.commit()
            flash('Book deleted successfully!', 'success')
            
    conn.close()
    return redirect(url_for('manage_books'))

# ---------------------------------------------------------------------------
# Staff Routes (Manage Users)
# ---------------------------------------------------------------------------
@app.route('/staff/users')
def manage_users():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users ORDER BY role, name')
        users = cursor.fetchall()
    conn.close()
    
    return render_template('users.html', users=users)

@app.route('/staff/users/add', methods=['POST'])
def add_user():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    phone = request.form.get('phone', '')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users (name, email, password, role, phone) VALUES (%s, %s, %s, %s, %s)',
                (name, email, password, role, phone)
            )
        conn.commit()
        flash(f'Account for {name} created successfully!', 'success')
    except pymysql.err.IntegrityError:
        flash('An account with this email already exists.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('manage_users'))

@app.route('/staff/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']
    phone = request.form.get('phone', '')
    password = request.form.get('password')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if password:
                cursor.execute(
                    'UPDATE users SET name = %s, email = %s, password = %s, role = %s, phone = %s WHERE id = %s',
                    (name, email, password, role, phone, id)
                )
            else:
                cursor.execute(
                    'UPDATE users SET name = %s, email = %s, role = %s, phone = %s WHERE id = %s',
                    (name, email, role, phone, id)
                )
        conn.commit()
        flash('User updated successfully!', 'success')
    except pymysql.err.IntegrityError:
        flash('Email address is already in use by another account.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('manage_users'))

@app.route('/staff/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    if id == session.get('user_id'):
        flash('You cannot delete your own active session account.', 'danger')
        return redirect(url_for('manage_users'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT count(*) as count FROM borrowings WHERE user_id = %s AND status = "Issued"', 
            (id,)
        )
        active_borrows = cursor.fetchone()['count']
        
        if active_borrows > 0:
            flash('Cannot delete user. They have books currently checked out.', 'danger')
        else:
            cursor.execute('DELETE FROM users WHERE id = %s', (id,))
            cursor.execute('DELETE FROM borrowings WHERE user_id = %s', (id,))
            conn.commit()
            flash('User account deleted successfully!', 'success')
            
    conn.close()
    return redirect(url_for('manage_users'))

# ---------------------------------------------------------------------------
# Staff Routes (Circulation Desk)
# ---------------------------------------------------------------------------
@app.route('/staff/circulation')
def circulation():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email FROM users WHERE role = 'student' ORDER BY name")
        students = cursor.fetchall()
        
        cursor.execute("SELECT id, title, available_copies FROM books WHERE available_copies > 0 ORDER BY title")
        available_books = cursor.fetchall()
        
        cursor.execute('''
            SELECT borrowings.id, users.name as student_name, books.title as book_title, 
                   borrowings.issue_date, borrowings.due_date 
            FROM borrowings 
            JOIN users ON borrowings.user_id = users.id 
            JOIN books ON borrowings.book_id = books.id 
            WHERE borrowings.status = 'Issued'
            ORDER BY borrowings.due_date ASC
        ''')
        active_borrows = cursor.fetchall()
        
    conn.close()
    
    return render_template('issue_return.html', students=students, books=available_books, borrows=active_borrows)

@app.route('/staff/circulation/issue', methods=['POST'])
def issue_book():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    user_id = request.form['user_id']
    book_id = request.form['book_id']
    
    issue_date = date.today()
    due_date = issue_date + timedelta(days=14)
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT available_copies FROM books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        
        if book and book['available_copies'] > 0:
            cursor.execute('''
                INSERT INTO borrowings (book_id, user_id, issue_date, due_date, status) 
                VALUES (%s, %s, %s, %s, 'Issued')
            ''', (book_id, user_id, issue_date, due_date))
            
            cursor.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id = %s', (book_id,))
            conn.commit()
            flash('Book issued successfully!', 'success')
        else:
            flash('Sorry, this book is currently out of stock.', 'danger')
            
    conn.close()
    return redirect(url_for('circulation'))

@app.route('/staff/circulation/return/<int:borrow_id>', methods=['POST'])
def return_book(borrow_id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    return_date = date.today()
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT book_id FROM borrowings WHERE id = %s', (borrow_id,))
        borrow = cursor.fetchone()
        
        if borrow:
            cursor.execute('''
                UPDATE borrowings 
                SET status = 'Returned', return_date = %s 
                WHERE id = %s
            ''', (return_date, borrow_id))
            
            cursor.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id = %s', (borrow['book_id'],))
            conn.commit()
            flash('Book returned successfully!', 'success')
            
    conn.close()
    return redirect(url_for('circulation'))

if __name__ == '__main__':
    app.run(debug=True)

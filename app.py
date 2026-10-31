import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from datetime import date, timedelta

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
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
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
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
    # Fetch metrics: total books, active users, overdue books, etc.
    books = conn.execute('SELECT * FROM books ORDER BY added_on DESC LIMIT 5').fetchall()
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
    # Fetch only the books borrowed by this specific student
    my_books = conn.execute('''
        SELECT books.title, books.author, borrowings.issue_date, borrowings.due_date, borrowings.status 
        FROM borrowings 
        JOIN books ON borrowings.book_id = books.id 
        WHERE borrowings.user_id = ?
    ''', (session['user_id'],)).fetchall()
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
    books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
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
        # For a new book, available copies equal total copies
        conn.execute('INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)',
                     (title, author, isbn, copies, copies))
        conn.commit()
        flash(f'"{title}" added successfully!', 'success')
    except sqlite3.IntegrityError:
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
    old_book = conn.execute('SELECT total_copies, available_copies FROM books WHERE id = ?', (id,)).fetchone()
    
    if old_book:
        # Calculate how the change in total copies affects available copies
        delta = new_total - old_book['total_copies']
        new_available = old_book['available_copies'] + delta
        
        if new_available < 0:
            flash('Cannot reduce total copies below the amount currently issued to students.', 'danger')
        else:
            try:
                conn.execute('''
                    UPDATE books 
                    SET title = ?, author = ?, isbn = ?, total_copies = ?, available_copies = ? 
                    WHERE id = ?
                ''', (title, author, isbn, new_total, new_available, id))
                conn.commit()
                flash('Book updated successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('ISBN already in use by another book.', 'danger')
    
    conn.close()
    return redirect(url_for('manage_books'))

@app.route('/staff/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # Prevent deletion if the book is currently checked out
    active_borrows = conn.execute('SELECT count(*) FROM borrowings WHERE book_id = ? AND status = "Issued"', (id,)).fetchone()[0]
    
    if active_borrows > 0:
        flash('Cannot delete book. Copies are currently issued to users.', 'danger')
    else:
        conn.execute('DELETE FROM books WHERE id = ?', (id,))
        # Clean up historical return records for this book to prevent orphaned data
        conn.execute('DELETE FROM borrowings WHERE book_id = ?', (id,))
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
    users = conn.execute('SELECT * FROM users ORDER BY role, name').fetchall()
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
        conn.execute(
            'INSERT INTO users (name, email, password, role, phone) VALUES (?, ?, ?, ?, ?)',
            (name, email, password, role, phone)
        )
        conn.commit()
        flash(f'Account for {name} created successfully!', 'success')
    except sqlite3.IntegrityError:
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
    
    # Optional password update
    password = request.form.get('password')
    
    conn = get_db_connection()
    try:
        if password:
            conn.execute(
                'UPDATE users SET name = ?, email = ?, password = ?, role = ?, phone = ? WHERE id = ?',
                (name, email, password, role, phone, id)
            )
        else:
            conn.execute(
                'UPDATE users SET name = ?, email = ?, role = ?, phone = ? WHERE id = ?',
                (name, email, role, phone, id)
            )
        conn.commit()
        flash('User updated successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Email address is already in use by another account.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('manage_users'))

@app.route('/staff/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    # Prevent a user from deleting their own account
    if id == session.get('user_id'):
        flash('You cannot delete your own active session account.', 'danger')
        return redirect(url_for('manage_users'))
        
    conn = get_db_connection()
    
    # Check for active borrows
    active_borrows = conn.execute(
        'SELECT count(*) FROM borrowings WHERE user_id = ? AND status = "Issued"', 
        (id,)
    ).fetchone()[0]
    
    if active_borrows > 0:
        flash('Cannot delete user. They have books currently checked out.', 'danger')
    else:
        conn.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.execute('DELETE FROM borrowings WHERE user_id = ?', (id,))
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
    
    # Get students for the dropdown
    students = conn.execute("SELECT id, name, email FROM users WHERE role = 'student' ORDER BY name").fetchall()
    
    # Get only books that are currently available to be checked out
    available_books = conn.execute("SELECT id, title, available_copies FROM books WHERE available_copies > 0 ORDER BY title").fetchall()
    
    # Get all currently issued books for the returns table
    active_borrows = conn.execute('''
        SELECT borrowings.id, users.name as student_name, books.title as book_title, 
               borrowings.issue_date, borrowings.due_date 
        FROM borrowings 
        JOIN users ON borrowings.user_id = users.id 
        JOIN books ON borrowings.book_id = books.id 
        WHERE borrowings.status = 'Issued'
        ORDER BY borrowings.due_date ASC
    ''').fetchall()
    
    conn.close()
    
    return render_template('issue_return.html', students=students, books=available_books, borrows=active_borrows)

@app.route('/staff/circulation/issue', methods=['POST'])
def issue_book():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
        
    user_id = request.form['user_id']
    book_id = request.form['book_id']
    
    issue_date = date.today()
    due_date = issue_date + timedelta(days=14) # Standard 14-day checkout
    
    conn = get_db_connection()
    
    # Double-check availability before inserting
    book = conn.execute('SELECT available_copies FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if book and book['available_copies'] > 0:
        # Create the borrowing record
        conn.execute('''
            INSERT INTO borrowings (book_id, user_id, issue_date, due_date, status) 
            VALUES (?, ?, ?, ?, 'Issued')
        ''', (book_id, user_id, issue_date, due_date))
        
        # Decrement available copies
        conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id = ?', (book_id,))
        
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
    
    # Get the book_id associated with this borrowing record
    borrow = conn.execute('SELECT book_id FROM borrowings WHERE id = ?', (borrow_id,)).fetchone()
    
    if borrow:
        # Mark as returned and set return date
        conn.execute('''
            UPDATE borrowings 
            SET status = 'Returned', return_date = ? 
            WHERE id = ?
        ''', (return_date, borrow_id))
        
        # Increment available copies
        conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id = ?', (borrow['book_id'],))
        
        conn.commit()
        flash('Book returned successfully!', 'success')
        
    conn.close()
    return redirect(url_for('circulation'))

if __name__ == '__main__':
    app.run(debug=True)
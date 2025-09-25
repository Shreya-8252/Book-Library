from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Book, Borrow
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        uid = session.get('user_id')
        user = None
        if uid:
            user = User.query.get(uid)
        if not user or not user.is_admin():
            flash("Admin access required.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('catalog'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','').strip()
        role = request.form.get('role','User')
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('signup.html')
        if User.query.filter((User.username==username)|(User.email==email)).first():
            flash("Username or email already exists.", "danger")
            return render_template('signup.html')
        user = User(username=username, email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username','').strip()
        pwd = request.form.get('password','').strip()
        user = User.query.filter_by(username=uname).first()
        if not user or not check_password_hash(user.password_hash, pwd):
            flash("Invalid credentials.", "danger")
            return render_template('login.html')
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        flash(f"Welcome, {user.username}!", "success")
        return redirect(url_for('catalog'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('login'))

@app.route('/catalog')
def catalog():
    books = Book.query.all()
    return render_template('catalog.html', books=books)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    user_borrowed = False
    if 'user_id' in session:
        user_id = session['user_id']
        user_borrowed = Borrow.query.filter_by(user_id=user_id, book_id=book.id, returned=False).first() is not None
    return render_template('book_detail.html', book=book, user_borrowed=user_borrowed)

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    user = User.query.get(session['user_id'])
    if book.available_copies() <= 0:
        flash("No copies available to borrow.", "danger")
        return redirect(url_for('book_detail', book_id=book.id))
    duplicate = Borrow.query.filter_by(user_id=user.id, book_id=book.id, returned=False).first()
    if duplicate:
        flash("You already borrowed this book. Return it before borrowing again.", "warning")
        return redirect(url_for('book_detail', book_id=book.id))
    borrow = Borrow(user_id=user.id, book_id=book.id)
    db.session.add(borrow)
    db.session.commit()
    flash(f"You borrowed '{book.title}'.", "success")
    return redirect(url_for('my_borrows'))

@app.route('/return/<int:borrow_id>', methods=['POST'])
@login_required
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    if borrow.user_id != session['user_id']:
        flash("Not authorized.", "danger")
        return redirect(url_for('catalog'))
    if borrow.returned:
        flash("Already returned.", "info")
        return redirect(url_for('my_borrows'))
    borrow.returned = True
    borrow.return_date = datetime.utcnow()
    db.session.commit()
    flash("Book returned. Thank you!", "success")
    return redirect(url_for('my_borrows'))

@app.route('/my-borrows')
@login_required
def my_borrows():
    user_id = session['user_id']
    borrows = Borrow.query.filter_by(user_id=user_id, returned=False).all()
    return render_template('my_borrows.html', borrows=borrows)

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    books = Book.query.all()
    return render_template('admin_dashboard.html', books=books)

@app.route('/admin/add', methods=['GET','POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        author = request.form.get('author','').strip()
        genre = request.form.get('genre','').strip()
        total_copies = request.form.get('total_copies','1').strip()
        if not title or not author:
            flash("Title and author required.", "danger")
            return render_template('add_book.html')
        try:
            total_copies = int(total_copies)
            if total_copies < 1:
                raise ValueError()
        except:
            flash("Total copies must be a positive integer.", "danger")
            return render_template('add_book.html')
        book = Book(title=title, author=author, genre=genre, total_copies=total_copies)
        db.session.add(book)
        db.session.commit()
        flash("Book added.", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_book.html')

@app.route('/admin/edit/<int:book_id>', methods=['GET','POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        author = request.form.get('author','').strip()
        genre = request.form.get('genre','').strip()
        total_copies = request.form.get('total_copies','1').strip()
        if not title or not author:
            flash("Title and author required.", "danger")
            return render_template('edit_book.html', book=book)
        try:
            total_copies = int(total_copies)
            if total_copies < 1:
                raise ValueError()
        except:
            flash("Total copies must be a positive integer.", "danger")
            return render_template('edit_book.html', book=book)
        book.title, book.author, book.genre, book.total_copies = title, author, genre, total_copies
        db.session.commit()
        flash("Book updated.", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_book.html', book=book)

@app.route('/admin/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.borrowed_count() > 0:
        flash("Cannot delete book while copies are borrowed.", "danger")
        return redirect(url_for('admin_dashboard'))
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted.", "info")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

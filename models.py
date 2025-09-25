from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='User')  # 'Admin' or 'User'
    borrows = db.relationship('Borrow', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'Admin'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(80))
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    borrows = db.relationship('Borrow', backref='book', lazy=True)

    def available_copies(self):
        # compute how many copies are available (not returned)
        borrowed_count = Borrow.query.filter_by(book_id=self.id, returned=False).count()
        return max(0, self.total_copies - borrowed_count)

    def borrowed_count(self):
        return Borrow.query.filter_by(book_id=self.id, returned=False).count()

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    returned = db.Column(db.Boolean, default=False)

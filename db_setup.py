from models import db, User, Book
from app import app
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com',
                         password_hash=generate_password_hash('admin123'),
                         role='Admin')
            db.session.add(admin)
        if Book.query.count() == 0:
            books = [
                Book(title='The Hobbit', author='J.R.R. Tolkien', genre='Fantasy', total_copies=3),
                Book(title='Atomic Habits', author='James Clear', genre='Self-help', total_copies=2),
                Book(title='Clean Code', author='Robert C. Martin', genre='Programming', total_copies=1),
            ]
            for b in books:
                db.session.add(b)
        db.session.commit()
        print("DB initialized and seeded (admin/admin123).")

if __name__ == '__main__':
    seed()

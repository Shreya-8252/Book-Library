import pytest
from app import app, db
from models import User, Book, Borrow
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            admin = User(username='admin', email='admin@x.com', password_hash=generate_password_hash('a'), role='Admin')
            user = User(username='u1', email='u1@x.com', password_hash=generate_password_hash('p'), role='User')
            book = Book(title='T', author='A', genre='G', total_copies=1)
            db.session.add_all([admin,user,book])
            db.session.commit()
        yield client

def login(client, username, password):
    return client.post('/login', data={'username':username, 'password':password}, follow_redirects=True)

def test_signup_login_logout(client):
    rv = client.post('/signup', data={'username':'newu','email':'n@x.com','password':'p'}, follow_redirects=True)
    assert b'Account created' in rv.data or b'Please login' in rv.data
    rv = login(client, 'newu', 'p')
    assert b'Welcome' in rv.data

def test_borrow_and_return(client):
    login(client, 'u1', 'p')
    rv = client.post('/borrow/1', follow_redirects=True)
    assert b'borrowed' in rv.data.lower() or b'You borrowed' in rv.data
    rv = client.post('/borrow/1', follow_redirects=True)
    assert b'already borrowed' in rv.data.lower() or b'already' in rv.data.lower()
    with app.app_context():
        b = Borrow.query.filter_by(user_id=2, book_id=1, returned=False).first()
        assert b is not None
        rv = client.post(f'/return/{b.id}', follow_redirects=True)
        assert b'returned' in rv.data.lower()

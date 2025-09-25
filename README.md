# Book Library (Flask + SQLite + HTML/CSS/JS)

This is a simple Book Library project using Flask (Python) for the backend, SQLite for the database, and HTML/CSS/JS for the frontend.

## create app
- A full Flask app with user signup/login (session-based), admin panel (add/edit/delete books), borrowing/returning flow, and templates.
- SQLite database (file `library.db` will be created when you run `db_setup.py`).
- Seed script (`db_setup.py`) to create the DB and add an `admin` user + sample books.
- Tests (`tests/test_basic.py`) using pytest.


## Quick steps to run (step-by-step)

1. Create and activate a virtual environment:
   - 
   - Windows (PowerShell):
     ```
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database and seed sample data (creates `library.db` and admin user `admin` / `admin123`):
   ```
   python db_setup.py
   ```
5. Run the app:
   ```
   python app.py
   ```
   Open your browser at: `http://127.0.0.1:5000`

6. Login as admin (to add/edit books):
   - Username: `admin`
   - Password: `admin123`

7. To run tests:
   ```
   pytest -q
   ```

## Key routes & functions (how they work)
- `app.py` contains Flask routes and logic.

### Authentication
- `/signup` (GET/POST): Create a new user. Stores `username`, `email`, and `password_hash`. Default role is `User`. Validates unique username/email.
- `/login` (GET/POST): Check credentials using `check_password_hash`. On success stores `user_id`, `username`, and `role` in `session`.
- `/logout`: Clears session.

### Catalog and  Book pages
- `/catalog`: Shows all books with available copies (`book.available_copies()`).
- `/book/<book_id>`: Shows details for a single book. If the user is logged in and copies available, shows a **Borrow** button.

### Borrow / Return
- `/borrow/<book_id>` (POST): Protected by `login_required`.
  - Checks if copies are available using `book.available_copies()`.
  - Prevents the same user from borrowing the same book if they haven't returned it.
  - Creates a `Borrow` record with `returned=False`.
- `/return/<borrow_id>` (POST): Protected by `login_required`.
  - Ensures the logged-in user owns the borrow record.
  - Sets `returned=True` and `return_date` to now.

## Admin
- `/admin`: Admin dashboard (protected by `admin_required`).
- `/admin/add`: Add a new book (title, author, genre, total_copies).
- `/admin/edit/<book_id>`: Edit book.
- `/admin/delete/<book_id>`: Delete book only if no active borrows (so you don't delete while copies are borrowed).

## Models (in `models.py`)
- `User`: `id, username, email, password_hash, role` and `is_admin()` helper.
- `Book`: `id, title, author, genre, total_copies` and helpers:
  - `available_copies()` — computes copies left by subtracting active borrows.
  - `borrowed_count()` — how many copies currently borrowed.
- `Borrow`: `id, user_id, book_id, borrow_date, return_date, returned` — tracks borrowing activity.

## you can implement
- Add CSRF protection (Flask-WTF) and use Flask-Login for production-ready auth.
- Improve UI with Bootstrap or Tailwind.
- Add search/pagination and borrow history pages.
- Add REST API endpoints if you want a separate frontend.

## ER DIAGRAM IN TEXT fORM
1. User Entity
ATTRIBUTES:
-id (Primary Key) – unique identifier for each user
-username – the username of the user
-email – the email address (unique)
-password_hash – the user’s password stored in hashed form
-role – defines the role (Admin or User)

RELATIONSHIPS:
 -One user can borrow many books.
 -Relationship: User (1) to Borrow (Many)

3. Book Entity
ATTRIBUTES:
-id (Primary Key) – unique identifier for each book
-title – the title of the book
-author – the author of the book
-genre – the genre/category of the book
-total_copies – the total number of copies available

RELATIONSHIPS:
One book can be borrowed many times.
Relationship: Book (1) to Borrow (Many)


3. Borrow Entity
ATTRIBUTES:
-id (Primary Key) – unique identifier for each borrow record
-user_id (Foreign Key → User.id) – which user borrowed the book
-book_id (Foreign Key → Book.id) – which book was borrowed
-borrow_date – when the book was borrowed
-return_date – when the book was returned (nullable if not returned yet)
-returned – Boolean (True/False) indicating if the book has been returned

RELATIONSHIPS:
-The Borrow table works as a bridge between Users and Books.
-It represents a many-to-many relationship between Users and Books.




## Summary:
User -> Borrow: One-to-Many
Book -> Borrow: One-to-Many
Together: Users and Books have a Many-to-Many relationship through the Borrow table.

# DEMO Video Link
i have uploaded the demo video on my youtube and below is the link :
Disclaimer:- Video is uploaded on my personal account
video link :- https://youtu.be/JP0DTTOxknI

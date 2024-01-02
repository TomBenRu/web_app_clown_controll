from database import db
from app import app


def start_database():
    db.start_db()


def run_application():
    app.run()


if __name__ == '__main__':
    start_database()
    run_application()

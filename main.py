from database import db
from app import app


db.start_db()
app.run()

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(300), nullable=False)
    thumbnail_url = db.Column(db.String(300))
    category = db.Column(db.String(100))
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

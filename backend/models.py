from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Patent(db.Model):
    __tablename__ = 'patents'

    id = db.Column(db.Integer, primary_key=True)
    publication_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text)
    description = db.Column(db.Text)
    assignee = db.Column(db.String(200))
    inventors = db.Column(JSONB)  # JSON 陣列
    priority_date = db.Column(db.Date)
    application_date = db.Column(db.Date)
    grant_date = db.Column(db.Date)
    claims = db.Column(JSONB)  # JSON 陣列
    jurisdictions = db.Column(db.String(50))
    classifications = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Patent {self.publication_number}>'

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    products = db.Column(JSONB)  # JSON 陣列
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Company {self.name}>'
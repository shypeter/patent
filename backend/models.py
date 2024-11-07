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
    inventors = db.Column(JSONB)
    priority_date = db.Column(db.Date)
    application_date = db.Column(db.Date)
    grant_date = db.Column(db.Date)
    claims = db.Column(JSONB)
    jurisdictions = db.Column(db.String(50))
    classifications = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Patent {self.publication_number}>'

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False) # also indexed
    products = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Company {self.name}>'

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    patent_publication_number = db.Column(db.String(50), nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False, index=True)
    analysis_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 使用 Index 創建聯合唯一索引
    __table_args__ = (
        db.Index('idx_patent_company_unique', 
                 'patent_publication_number', 
                 'company_name', 
                 unique=True),
    )

    def __repr__(self):
        return f'<Report {self.id}>'
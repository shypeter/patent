from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS  
from models import db
from os import environ

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    Migrate(app, db)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
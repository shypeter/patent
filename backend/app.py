from flask import Flask, request, jsonify, make_response
from flask_cors import CORS  
from models import db, Patent, Company
from os import environ
from analysis import PatentAnalyzer
from datetime import datetime

# Create the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize the PatentAnalyzer
PatentAnalyzer(openai_api_key=environ.get('OPENAI_API_KEY'))

# test route
@app.route('/test', methods=['GET'])
def test():
  return jsonify({'message': 'The server is running'})

@app.route('/api/patents', methods=['GET'])
def get_patents():
    try:
        patents = Patent.query.all()
        patents_data = [{
            'publication_number': patent.publication_number,
            'title': patent.title
            } for patent in patents
        ]
        return jsonify(patents_data), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error getting patents', 'error': str(e)}), 500)

@app.route('/api/companies', methods=['GET'])
def get_companies():
    try:
        companies = Company.query.all()
        companies_data = [{
            'id': company.id,
            'name': company.name,
            'products': company.products
            } for company in companies
        ]
        return jsonify(companies_data), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error getting companies', 'error': str(e)}), 500)

@app.route('/api/patent/<id>', methods=['GET'])
def get_patent_details(id):
    try:
        patent = Patent.query.filter_by(publication_number=id).first()
        if not patent:
            return make_response(jsonify({
                'message': 'patent not found'
                }), 404)

        return make_response(jsonify({
            'publication_number': patent.publication_number,
            'title': patent.title,
            'abstract': patent.abstract,
            'description': patent.description,
            'assignee': patent.assignee,
            'inventors': patent.inventors,
            'priority_date': patent.priority_date,
            'application_date': patent.application_date,
            'grant_date': patent.grant_date,
            'claims': patent.claims,
            'jurisdictions': patent.jurisdictions,
            'classifications': patent.classifications
            }), 200)
    except Exception as e:
        return make_response(jsonify({
            'error': str(e)
            }), 500)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

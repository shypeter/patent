import json
from datetime import datetime
from app import create_app
from models import db, Patent, Company
import sys

def parse_data(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError: 
        return None
    
def import_patents(file_path):
    print("start import patents")
    with open(file_path, 'r', encoding='utf-8') as file:
        parents_data = json.load(file)

    for patent_data in parents_data:
        patent = Patent(
            publication_number=patent_data['publication_number'],
            title=patent_data['title'],
            abstract=patent_data['abstract'],
            description=patent_data['description'],
            assignee=patent_data['assignee'],
            inventors=patent_data['inventors'],
            priority_date=parse_data(patent_data['priority_date']),
            application_date=parse_data(patent_data['application_date']),
            grant_date=parse_data(patent_data['grant_date']),
            claims=patent_data['claims'],
            jurisdictions=patent_data['jurisdictions'],
            classifications=patent_data['classifications']
        )
        db.session.add(patent)
    
    try:
        db.session.commit()
        print('Patents imported successfully')
    except Exception as e:
        db.session.rollback()
        print(f'Error importing patents: {str(e)}')


def import_companies(file_path):
    print("start import companies")
    with open(file_path, 'r', encoding='utf-8') as file:
        companies_data = json.load(file)

    for company_data in companies_data["companies"]:
        company = Company(
            name=company_data['name'],
            products=company_data['products']
        )
        db.session.add(company)
    
    try:
        db.session.commit()
        print('Companies imported successfully')
    except Exception as e:
        db.session.rollback()
        print(f'Error importing companies: {str(e)}')

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        import_patents('patents.json')
        import_companies('company_products.json')
        sys.exit(0)
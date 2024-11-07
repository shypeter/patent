import json
import psycopg2
from datetime import datetime
from psycopg2.extras import Json

def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def connect_db():
    """Create database connection"""
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="db",
        port="5432"
    )

def create_tables(conn):
    """Create necessary tables if they don't exist"""
    with conn.cursor() as cur:
        # Create patents table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patents (
                id SERIAL PRIMARY KEY,
                publication_number VARCHAR(100) UNIQUE NOT NULL,
                title VARCHAR(500),
                abstract TEXT,
                description TEXT,
                assignee VARCHAR(200),
                inventors TEXT,
                priority_date DATE,
                application_date DATE,
                grant_date DATE,
                claims TEXT,
                jurisdictions VARCHAR(100),
                classifications TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create companies table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                products JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create reports table with indexes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                patent_publication_number VARCHAR(50) NOT NULL,
                company_name VARCHAR(200) NOT NULL,
                analysis_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create individual indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_patent_publication_number 
            ON reports(patent_publication_number)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_name 
            ON reports(company_name)
        """)

        # Create unique compound index
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_patent_company_unique 
            ON reports(patent_publication_number, company_name)
        """)
        
        conn.commit()

def import_patents(conn, file_path):
    """Import patents from JSON file"""
    print("Importing patents...")
    with open(file_path, 'r', encoding='utf-8') as file:
        patents_data = json.load(file)

    with conn.cursor() as cur:
        for patent in patents_data:
            cur.execute("""
                INSERT INTO patents (
                    publication_number, title, abstract, description,
                    assignee, inventors, priority_date, application_date,
                    grant_date, claims, jurisdictions, classifications
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (publication_number) DO NOTHING
            """, (
                patent['publication_number'],
                patent['title'],
                patent['abstract'],
                patent['description'],
                patent['assignee'],
                patent['inventors'],
                parse_date(patent['priority_date']),
                parse_date(patent['application_date']),
                parse_date(patent['grant_date']),
                patent['claims'],
                patent['jurisdictions'],
                patent['classifications']
            ))
        
        conn.commit()
    print("Patents imported successfully")

def import_companies(conn, file_path):
    """Import companies from JSON file"""
    print("Importing companies...")
    with open(file_path, 'r', encoding='utf-8') as file:
        companies_data = json.load(file)

    with conn.cursor() as cur:
        for company in companies_data['companies']:
            cur.execute("""
                INSERT INTO companies (name, products)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
            """, (
                company['name'],
                Json(company['products'])
            ))
        
        conn.commit()
    print("Companies imported successfully")


def main():
    try:
        # Connect to database
        conn = connect_db()
        
        # Create tables
        create_tables(conn)
        print("Tables created successfully!")

        # Import data
        import_patents(conn, 'patents.json')
        import_companies(conn, 'company_products.json')
        print("All data imported successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
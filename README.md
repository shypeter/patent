flask + nextjs + postgres + docker
##
put company_products.json and patents.json to `backend` folder.

## install
```
docker-compose build
docker-compose up -d
```

## parse json data to postgres
```
docker exec -it flaskapp python import_data.py
```

# API doc
```
swagger.yaml
```

# Database Schema
## Patents Table

Stores patent information and related metadata.

| Column Name | Data Type | Constraints |
|------------|-----------|-------------|
| id | Integer | Primary Key |
| publication_number | String(50) | Unique, Not Null |
| title | String(500) | Not Null |
| abstract | Text | - |
| description | Text | - |
| assignee | String(200) | - |
| inventors | JSONB | - |
| priority_date | Date | - |
| application_date | Date | - |
| grant_date | Date | - |
| claims | JSONB | - |
| jurisdictions | String(50) | - |
| classifications | JSONB | - |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now(), Auto-update |

## Companies Table

Stores company information and their products.

| Column Name | Data Type | Constraints |
|------------|-----------|-------------|
| id | Integer | Primary Key |
| name | String(200) | Unique, Not Null, Indexed |
| products | JSONB | - |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now(), Auto-update |

## Reports Table

Stores patent infringement analysis reports.

| Column Name | Data Type | Constraints |
|------------|-----------|-------------|
| id | Integer | Primary Key |
| patent_publication_number | String(50) | Not Null, Indexed |
| company_name | String(200) | Not Null, Indexed |
| analysis_data | JSONB | - |
| created_at | DateTime | Default: now() |

### Indexes

The Reports table includes the following indexes:
- Combined unique index on `patent_publication_number` and `company_name` (named: idx_patent_company_unique)
- Individual indexes on `patent_publication_number` and `company_name`

flask + nextjs + docker
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
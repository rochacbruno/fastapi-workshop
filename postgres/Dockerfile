FROM postgres:alpine3.14
# Uncomment to use Mac M1
# FROM --platform=linux/amd64 postgres:alpine3.14 
COPY create-databases.sh /docker-entrypoint-initdb.d/

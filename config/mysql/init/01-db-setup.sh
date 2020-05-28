#!/bin/sh

psql -U postgres -c "CREATE USER $POSTGRES_USER PASSWORD '$POSTGRES_PASSWORD'"
psql -U postgres -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER"

create database auth_db;
#CREATE USER 'auth_admin'@'localhost' IDENTIFIED BY 'Monday#123';
#GRANT ALL PRIVILEGES ON auth_db . * TO 'auth_admin'@'localhost’;

CREATE USER 'auth_admin'@'%' IDENTIFIED BY $1;
GRANT ALL PRIVILEGES ON auth_db . * TO 'auth_admin'@'%';


docker exec -it $2 python manage.py createsuperuser\
# sudo chmod u+x setup.sh
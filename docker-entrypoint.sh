#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate


create database auth_db;
#CREATE USER 'auth_admin'@'localhost' IDENTIFIED BY 'Monday#123';
#GRANT ALL PRIVILEGES ON auth_db . * TO 'auth_admin'@'localhost’;

CREATE USER 'auth_admin'@'%' IDENTIFIED BY $1;
GRANT ALL PRIVILEGES ON auth_db . * TO 'auth_admin'@'%';


docker exec -it $2 python manage.py createsuperuser
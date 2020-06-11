.PHONY: all build push deploy run stop

all: build push deploy

build:
	docker build -t umeshvjti/auth-service:latest -f .

push:
	docker push umeshvjti/auth-service:latest

deploy:
	eb deploy

run:
	docker-compose up -d

stop:
	docker-compose down
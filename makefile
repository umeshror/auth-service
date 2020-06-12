.PHONY: all build push deploy run stop

all: build push deploy

build:
	docker build -t umeshvjti/auth-service:latest -f .

build-docker:
	docker build -t umeshvjti/auth-service:latest -f .

build-aws:
	docker build -t 487489065118.dkr.ecr.us-east-2.amazonaws.com/auth-service -f .

push:
	docker push umeshvjti/auth-service:latest

deploy:
	eb deploy

run:
	docker-compose up -d

stop:
	docker-compose down
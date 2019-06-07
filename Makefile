SHELL := /bin/bash
USER   := $(shell id -un)
LOGDIRECTORY := tmp/logs
VERSION := latest
PORT := 8082
FLASK_ENV := production
FLASK_APP := myapp.py
CONTAINER := flask-$(USER)

build:
	# Check if image is built
	docker build -t flask-testing/flask-base:$(VERSION) .


run-container: build
	# Check for container running
	docker run -d -t --name=$(CONTAINER) -p $(PORT):5000 \
		-e "LOGDIRECTORY=$(LOGDIRECTORY)" -e "FLASK_APP=$(FLASK_APP)" \
		-e "FLASK_ENV=$(FLASK_ENV)" -e "LC_ALL=C.UTF-8" -e "LANG=C.UTF-8" \
		--workdir=$(PWD) --volume $(PWD):$(PWD) \
		flask-testing/flask-base:$(VERSION)

run-app: run-container
	docker exec -t $(CONTAINER) flask run --host 0.0.0.0 --reload &

stop-app:
	# Check if container is running
	# Check if app is running
	# Stop the running app http://flask.pocoo.org/snippets/67/

run-test: run-container
	docker exec -t $(CONTAINER) flask test

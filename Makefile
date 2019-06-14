SHELL := /bin/bash
USER   := $(shell id -un)
LOGDIRECTORY := tmp/logs
VERSION := latest
PORT := 8082
FLASK_ENV := production
FLASK_APP := rest.py
CONTAINER := flask-$(USER)
IMAGE_EXISTS=$(shell docker images -q flask-testing/flask-base:$(VERSION))

build:
	# Check if image is built
	if [[ "$(IMAGE_EXISTS)" == "" ]]; then \
		docker build -t flask-testing/flask-base:$(VERSION) .; \
	else \
		echo Image is available locally.; \
	fi

run-container: build
	# Check for container running
	if  [[ $(shell docker ps | grep $(CONTAINER)| wc -l) == 0 ]]; then \
		docker run -d -t --name=$(CONTAINER) -p $(PORT):5000 \
			-e "LOGDIRECTORY=$(LOGDIRECTORY)" -e "FLASK_APP=$(FLASK_APP)" \
			-e "FLASK_ENV=$(FLASK_ENV)" -e "LC_ALL=C.UTF-8" -e "LANG=C.UTF-8" \
			-e "PYTHONPATH=$(PWD)/src" \
			--workdir=$(PWD)/src --volume $(PWD):$(PWD) \
			flask-testing/flask-base:$(VERSION); \
	else \
		echo Container $(CONTAINER) is already running; \
	fi

run-app: stop-container run-container
	docker exec -t $(CONTAINER) flask run --host 0.0.0.0 --reload &

stop-container:
	docker rm -f $(CONTAINER)  2>/dev/null||true;

stop-app: stop-container
	# Check if container is running
	# Check if app is running
	# Stop the running app http://flask.pocoo.org/snippets/67/

run-test: run-container
	docker exec -t $(CONTAINER) flask test

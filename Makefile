PYTHON := python3
APP_NAME := bx24
APP_LOG := interaction.log
SOAP_LOG := emulation/server.log
COMMON_LOG := common.save.log

help: # This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

soap: ## Bitrix API emulation.
	nohup $(PYTHON) emulation/server.py >> $(SOAP_LOG) &

show_soap_methods: ## Shows `LocalBitrix` methods.
	$(PYTHON) emulation/client.py

app: ## Open root page in browser.
	nohup google-chrome http://127.0.0.1:5000/ >> chrome.log &

style: ## Check styles with flake8.
	flake8 .

typos: ## Check types with mypy.
	mypy .

check: ## Check styles and types.
	make style typos

update_log: ## Dump all logs into common.save.log and clean up.
	@test -f $(APP_LOG) || touch $(APP_LOG)
	@test -f $(SOAP_LOG) || touch $(SOAP_LOG)
	@cat $(APP_LOG) $(SOAP_LOG) >> $(COMMON_LOG) && >$(APP_LOG) && >$(SOAP_LOG)

run: ## Run Flask app.
	nohup $(PYTHON) app.py >> $(APP_LOG) &

r: update_log ## Update logs and start program with `LocalBitrix`(api emulation).
	make soap run

clean1 clean2 &: ## Returns emulation/scm/**/list.json files to its original state.
	@$(PYTHON) -c "file1, file2 = 'emulation/crm/contacts/list.json', 'emulation/crm/deal/list.json';\
	f1,f2 = open(file1, 'w'),open(file2, 'w'); f1.write('{\"contacts\":[]}\n'); f2.write('{\"deal\":[]}\n')"

test: ## Run tests (Flask running).
	$(PYTHON) tests.py

t: r ## Run Flask app and tests.
	sleep 5; make test

check_connects: ## Active Internet connections.
	netstat -tulpn

kill_soap: ## Kill Soap server PID (Bitrix emulation).
	kill `lsof -t -i:8000` || true

kill_app: ## Kill Flask app PID.
	kill `lsof -t -i:5000` || true

kill_all: ## Kill Soap server and Flask app.
	make kill_soap kill_app

reload: ## Reload Flask app.
	make kill_all r

retest: clean1 ## Clear logs and other data and restart tests.
	make kill_all t

git: check retest clean2 ## make git m="message"
	git add .
	git commit -m "$m"
	git push -u origin main

warnings:  ## Check dev artifacts.
	grep --color="always" --include="*.py" -i -r -n -w . -e 'print\|fixme\|refactorme'

docker_start: ## Docker start if Docker not starting.
	sudo service docker status > /dev/null || sudo service docker start

docker_build: ## Build the container with `APP_NAME` tag.
	docker build --tag $(APP_NAME) .

docker_build_nc: ## Build the container without caching.
	docker build --no-cache --tag $(APP_NAME) .

# --detach, -t - Run container in background and print container ID.
# --tty, -t - Allocate a pseudo-TTY.
# --rm - Automatically remove the container when it exits.
docker_run:  ## Run (-dt --rm) Docker container with environment variables.
	docker run --detach --tty --rm \
	--env WSDL_URL \
	--env BITRIX_EMULATION \
	--env CBR_URL \
	--env COMPANY \
	--env USER_ID \
	--env SECRET_TOKEN \
	--env FLASK_APP \
	--env FLASK_DEBUG \
	--env FLASK_ENV \
	--name "$(APP_NAME)" $(APP_NAME)

docker_bash: ## Execute an interactive bash shell on the container.
	docker exec -it $(APP_NAME) /bin/bash

up: docker_start docker_build docker_run ## Build and run Dockerfile with one command.

docker_rm: ## Stop and remove a running container.
	docker stop $(APP_NAME); docker rm $(APP_NAME)

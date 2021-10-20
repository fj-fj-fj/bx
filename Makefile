APP_NAME := bx24
APP_LOG := interaction.log
SOAP_LOG := emulation/server.log
COMMON_LOG := common.save.log

VENV := ../.venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

ifndef VERBOSE
MAKEFLAGS += --no-print-directory
endif

help: # This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Clone repo into bx/src/, create .venv into bx/ and pip install requirements.
	mkdir bx \
	&& git -C ./bx clone https://github.com/fj-fj-fj/bx.git src\
	&& $(PYTHON) -m venv bx/.venv \
	&& bx/.venv/bin/pip install -r bx/src/requirements.txt

# `venv` sets the environment variable `$VIRTUAL_ENV` when activating an environment.
# This only works when the environment is activated by the activate shell script.
check_virtual_env: ## Determine if Python is running inside virtualenv.
	@echo $${VIRTUAL_ENV?"[ERROR]: Virtual environment not activated!"}

# Whenever requirements.txt changes, it rebuilds the environment and
# installs the dependencies with pip, which re-creates the activate.
# NOTE: will install -r requirements.txt -r emulation/requirements.txt -r requirements/lint.txt
$(VENV)/bin/activate: requirements.txt ## Automatically refresh $(VENV) and pip reinstall whenever the requirements.txt file changes.
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

soap: ## Bitrix API emulation.
	nohup $(PYTHON) emulation/server.py >> $(SOAP_LOG) &

show_soap_methods: ## Shows available Bitrix methods.
	$(PYTHON) emulation/client.py

browse: ## Open root page in browser (google-chrome).
	nohup google-chrome http://127.0.0.1:5000/ >> chrome.log &

style: ## Check styles with flake8.
	$(VENV)/bin/flake8 --max-line-length=100 --exclude data .

typos: ## Check types with mypy.
	$(VENV)/bin/mypy --allow-redefinition --ignore-missing-imports --exclude data .

check: ## Check styles and types.
	make style typos

update_log: ## Dump all logs into common.save.log and clean up.
	@test -f $(APP_LOG) || touch $(APP_LOG)
	@test -f $(SOAP_LOG) || touch $(SOAP_LOG)
	@cat $(APP_LOG) $(SOAP_LOG) >> $(COMMON_LOG) && >$(APP_LOG) && >$(SOAP_LOG)

run: $(VENV)/bin/activate ## Run app with virtual environment.
	nohup $(PYTHON) app.py >> $(APP_LOG) &

r: update_log ## Update logs, start Bitrix emulation and app.
	make soap run

clean1 clean2 &: ## Returns emulation/scm/**/list.json files to its original state.
	@$(PYTHON) -c "file1, file2 = 'emulation/crm/contacts/list.json', 'emulation/crm/deal/list.json';\
	f1,f2 = open(file1, 'w'),open(file2, 'w'); f1.write('{\"contacts\":[]}\n'); f2.write('{\"deal\":[]}\n')"

clean_pyc: ## Clean up old *.py[cod] files.
	find -name \*.py[cod] -print0 | xargs -0 rm -f

# WARNING: Not all environments have bash available.
test: $(eval SHELL:=/bin/bash) ## Run tests (requires a running Flask).
	@if [ $$(date +"%M") == "00" ]; then \
		echo "TESTS WILL FAIL NOW: try in a munute! \
	(See \`replace_minutes_and_seconds()\` in tests.py)"; \
	else \
		$(PYTHON) tests.py; \
	fi

t: r ## Run Flask app and tests.
	sleep 5; make test

check_connects: ## Active Internet connections.
	netstat -tulpn

kill_soap: ## Kill Soap server PID (Bitrix emulation).
	@kill `lsof -t -i:8000` 2>/dev/null || true

kill_app: ## Kill Flask app PID.
	@kill `lsof -t -i:5000` 2>/dev/null || true

kill_all: ## Kill Soap server and Flask app.
	@make kill_soap kill_app

reload: ## Reload Flask app.
	@make kill_all r

retest: clean1 ## Clear logs and other data and restart tests.
	@make kill_all t

# cntl+c to break at any monent.
# WARNING: after 23:00 (central bank latest update) Moscow time, tests will not pass.
git: check retest clean2 ## Pre-push hook with "interprocess communication" (make git m="message").
	@python3 -c "import os; os.system('git diff' if input('git diff: [Y/n]') in 'Yy' else '')"
	git add . && git status
	@python3 -c "import os; os.system(input())"
	git commit -m "$m" && git log -1
	@python3 -c "import os; os.system('git reset --soft HEAD~1' if input('Undo last commit: [Y/n]') in 'Yy' else '')"
	@python3 -c "import os; os.system('git push -u origin main' if input('git push: [Y/n]') in 'Yy' else '')"

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
docker_run:  ## Run (-dt --rm) the container with environment variables.
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
	--env TZ=$$(cat /etc/timezone) \
	--name "$(APP_NAME)" $(APP_NAME)

docker_bash: ## Execute an interactive bash shell on the container.
	docker exec -it $(APP_NAME) /bin/bash

up: docker_start docker_build docker_run ## Build and run Dockerfile with one command.

docker_rm: ## Stop and remove a running container.
	docker stop $(APP_NAME); docker rm $(APP_NAME)

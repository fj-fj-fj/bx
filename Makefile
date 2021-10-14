PYTHON := python3

soap: ## Bitrix API emulation.
	nohup $(PYTHON) emulation/server.py >> emulation/server.log &

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

update_log: ## Dupm all logs into common.save.log and clean up.
	@cat emulation/server.log app.log >> common.save.log \
	&& >app.log && >emulation/server.log

run: ## Run Flask app.
	nohup $(PYTHON) app.py >> app.log &

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

warnings:
	grep --color="always" --include="*.py" -i -r -n -w . -e 'print\|fixme\|refactorme'

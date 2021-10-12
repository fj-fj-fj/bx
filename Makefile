PYTHON := python3

soap: ## Bitrix API emulation
	nohup $(PYTHON) emulation/server.py >> emulation/server.log &

show_soap_methods: ## Shows `LocalBitrix` methods
	$(PYTHON) emulation/client.py

style:
	flake8 .

typos:
	mypy .

check:
	make style typos

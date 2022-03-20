.PHONY: install debug

install:
	python3 -m pip install -r requirements.txt

debug:
	DEBUG=1
	python3 src/main.py

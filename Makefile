
.PHONY: all get-bottle serve

all: get-bottle serve


get-bottle:
	test -f bottle.py || curl https://raw.githubusercontent.com/bottlepy/bottle/master/bottle.py -o bottle.py

serve:
	python3 data-source.py

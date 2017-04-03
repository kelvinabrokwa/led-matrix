CURR_DIR := $(shell pwd)
PY_VENV := "pyvenv"
PYTHON := $(PY_VENV)/bin/python
PIP := $(PYTHON) -m pip
NODE_MODULES := web/node_modules

setup: setup-py setup-web

setup-py: $(PY_VENV)
	virtualenv -p python3 pyenv
	$(PIP) install -r requirements.txt
	git submodule update --init --recursive
	cd rpi-rgb-led-matrix/bindings/python
	make build-python
	sudo make install-python

setup-web: $(NODE_MODULES)
	cd web
	npm install
	npm run build

install:
	ln -s $(CURR_DIR)/nginx.conf /etc/nginx/sites-enabled/led-matrix.com

clean:
	rm -rf $(PY_VENV) $(NODE_MODULES)

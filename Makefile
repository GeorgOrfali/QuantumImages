run:
	python3 main.py
setup:
	python3 -m pip install --upgrade pip
	sudo apt install python3-tk
	pip install netsquid --extra-index-url https://pypi.netsquid.org
	pip install -r requirements.txt
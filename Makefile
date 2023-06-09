run:
	python main.py
setup:
	python -m pip install --upgrade pip
	pip install netsquid --extra-index-url https://pypi.netsquid.org
	pip install -r requirements.txt
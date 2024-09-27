run:
	python3 main.py
runtime:
	python3 -m cProfile -o time.prof -s time main.py
readtime:
	python -m pstats time.prof
setup:
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt
clean:
	pip uninstall -r requirements.txt -y
	pip uninstall qiskit-terra
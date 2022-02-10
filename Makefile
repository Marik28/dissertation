install:
	pip install -U pip setuptools
	pip install -r requirements.txt

notebook:
	jupyter notebook

make run-gui:
	cd src; python -m dissertation_gui
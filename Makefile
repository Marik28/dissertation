install:
	pip install -U pip setuptools
	pip install -r requirements.txt

notebook:
	jupyter notebook

run-gui:
	cd src; python -m dissertation_gui

makemigrations:
	cd src; alembic revision --autogenerate

migrate:
	cd src; alembic upgrade head

fill-database:
	cd src; python -m scripts.fill_database
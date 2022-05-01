install:
	pip install -U pip setuptools
	pip install -r requirements.txt

notebook:
	jupyter notebook

run-gui:
	cd src; python3 -m dissertation_gui

makemigrations:
	cd src; alembic revision --autogenerate

migrate:
	cd src; alembic upgrade head

fill-database:
	cd src; python3 -m scripts.fill_database

drop-database:
	rm src/dissertation_gui/db.sqlite3

available-ports:
	python3 -m serial.tools.list_ports

generate-dataframes:
	cd src; python3 -m scripts.generate_dfs
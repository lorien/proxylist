.PHONY: bootstrap venv deps dirs clean pytest test release mypy pylint flake8 bandit check build coverage docs

FILES_CHECK_MYPY = proxylist tests
FILES_CHECK_ALL = $(FILES_CHECK_MYPY)

bootstrap: venv deps dirs

venv:
	virtualenv -p python3 .env

deps:
	.env/bin/pip install -r requirements_dev.txt
	.env/bin/pip install -e .

dirs:
	if [ ! -e var/run ]; then mkdir -p var/run; fi
	if [ ! -e var/log ]; then mkdir -p var/log; fi

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete
	find -name '__pycache__' -delete

pytest:
	pytest --cov proxylist --cov-report term-missing

test:
	make check \
	&& make pytest \
	&& tox -e py38-check


release:
	git push \
	&& git push --tags \
	&& make build \
	&& twine upload dist/*

mypy:
	mypy --strict $(FILES_CHECK_MYPY)

pylint:
	pylint -j0 $(FILES_CHECK_ALL)

flake8:
	flake8 -j auto --max-cognitive-complexity=17 $(FILES_CHECK_ALL)

bandit:
	bandit -qc pyproject.toml -r $(FILES_CHECK_ALL)

check:
	echo "mypy" \
	&& make mypy \
	&& echo "pylint" \
	&& make pylint \
	&& echo "flake8" \
	&& make flake8 \
	&& echo "bandit" \
	&& make bandit

build:
	rm -rf *.egg-info
	rm -rf dist/*
	python -m build --sdist

coverage:
	pytest --cov proxylist --cov-report term-missing

docs:
	rm -rf docs/_build/html 
	sphinx-build -j auto docs docs/_build/html

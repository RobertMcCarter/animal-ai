install:
	pip install --upgrade pip &&\
		pip install pipenv &&\
		pipenv install

test:
	# See: https://docs.pytest.org/en/6.2.x/
	python -m pytest -vv --cov=src src/*_test.py

format:
	black src/*.py test/*.py

lint:
	pylint --disable=R,C,W1203,E1101 mlib cli src/*.py
	#lint Dockerfile
	#docker run --rm -i hadolint/hadolint < Dockerfile

all: install lint test

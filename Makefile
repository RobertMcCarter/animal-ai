install:
	pip install --upgrade pip &&\
		pip install pipenv &&\
		pipenv install

test:
	python -m pytest -vv --cov=cli --cov=mlib --cov=utilscli src/*_test.py

format:
	black src/*.py

lint:
	pylint --disable=R,C,W1203,E1101 mlib cli utilscli
	#lint Dockerfile
	#docker run --rm -i hadolint/hadolint < Dockerfile

all: install lint test

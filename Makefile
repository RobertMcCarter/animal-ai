install:
	pip install --upgrade pip &&\
		pip install pipenv &&\
		pipenv install

format:
	# Use black (https://black.readthedocs.io/en/stable/)
	# to format the code according to PEP 8
	black src/*.py       src/**/*.py \
	      test/*.py      test/**/*.py \
		  tagger_ui/*.py tagger_ui/**/*.py \
		  utils/*.py     utils/**/*.py

lint:
	pylint --disable=R,C,W1203,E1101 mlib cli src/*.py
	#lint Dockerfile
	#docker run --rm -i hadolint/hadolint < Dockerfile

unittest:
	# Run all of the unit tests
	python -m unittest discover --verbose --start-directory ./test/ --pattern *_test.py

tagui:
	# Run the Python UI for tagging and selecting regions in the images
	python tagger_ui/tk_data_annotator_ui.py

imageex:
	# Run the Python tool for extracting true/false tagged images from the animals.json data file
	python src/training_sub_image_extraction.py

all: install lint test

ON_TAG := $(shell git tag --points-at HEAD)

.PHONY: test wheel publish maybe_publish docs

all: test wheel

test:
	pip install pytest
	pytest .

wheel: test
	rm -rf build dist
	pip install -U wheel
	python setup.py bdist_wheel

docs:
	pip install sphinx
	(cd docs; make html)

publish: wheel
	pip install twine
	twine upload dist/*.whl -u __token__ -p $(PYPI_TOKEN)

maybe_publish:
ifneq ($(ON_TAG),)
	pip install twine
	twine upload dist/pdfbrain*.whl -u __token__ -p $(PYPI_TOKEN)
endif

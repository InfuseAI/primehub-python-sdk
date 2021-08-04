default: test-html


dev-requires:
	pip install -e .[dev]

test: dev-requires
	py.test --cov=primehub --cov-report xml --flake8 --mypy

test-html: dev-requires
	py.test --cov=primehub --cov-report html --flake8 --mypy

test-regression:
	PRIMEHUB_SDK_DEVLAB=true primehub e2e basic-functions

docs: dev-requires
	doc-primehub

pre-release: dev-requires
	python3 -m build
	python3 -m twine upload --repository testpypi dist/*

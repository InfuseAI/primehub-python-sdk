default: test-html


dev-requires:
	pip install -e .[dev]

test: dev-requires
	py.test --cov=primehub --cov-report xml --flake8 --mypy --ignore=tests/test_graphql_lint.py

test-html: dev-requires
	py.test --cov=primehub --cov-report html --flake8 --mypy --ignore=tests/test_graphql_lint.py

test-regression:
	PRIMEHUB_SDK_DEVLAB=true primehub e2e basic-functions

test-gql: dev-requires
	py.test tests/test_graphql_lint.py

docs: dev-requires
	doc-primehub

pre-release: dev-requires
	pip install build
	python3 -m build
	python3 -m twine upload --repository testpypi dist/*

release: dev-requires
	pip install build
	python3 -m build
	python3 -m twine upload dist/*

dev-requires:
	pip install -e .[dev]

test: dev-requires
	py.test --cov=primehub --cov-report xml --flake8 --mypy

test-html: dev-requires
	py.test --cov=primehub --cov-report html --flake8 --mypy


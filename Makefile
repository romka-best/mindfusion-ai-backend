.PHONY: ruff style test lint all poetry-check git-branch-check

package?=bot

all: style lint deptry test

style:
	ruff format $(package)
	ruff check --select I --fix $(package)

mypy:
	mypy $(package)

ruff:
	ruff format --check --diff $(package)
	ruff check $(package)

lint: ruff git-branch-check deptry

test: lint
	pytest --cov=app -n auto .

deptry:
	deptry .

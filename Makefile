.PHONY: install run test

install:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	python -m pytest -q

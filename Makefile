.PHONY: install run frontend test

install:
	python -m pip install -r requirements.txt
	python -m pip install -e .

run:
	uvicorn incident_agent.api.main:app --app-dir src --reload --port 8000

frontend:
	cd frontend && npm install && npm run dev

test:
	pytest -q

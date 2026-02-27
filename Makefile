PYTHON ?= python3

.PHONY: test check clean clean-examples run

test:
	$(PYTHON) -m pytest tests/ -x -q

check: test
	$(PYTHON) -m compileall -q swe_af/
	$(PYTHON) -m compileall -q src/able_to_answer/

run:
	$(PYTHON) -m uvicorn able_to_answer.api.main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -path "./.git" -prune -o -path "./.venv" -prune -o -type f \( -name "*.pyc" -o -name ".DS_Store" -o -name "*.bak" \) -delete
	find . -path "./.git" -prune -o -path "./.venv" -prune -o -depth -type d -name "__pycache__" -empty -delete

clean-examples:
	if [ -d examples/diagrams/target ]; then find examples/diagrams/target -depth -mindepth 1 -delete; rmdir examples/diagrams/target || true; fi
	if [ -d examples/pyrust/target ]; then find examples/pyrust/target -depth -mindepth 1 -delete; rmdir examples/pyrust/target || true; fi

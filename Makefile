ENV_FILE := ${PWD}/.env


test:
	@echo "Running tests..."
	@uv run --env-file ${ENV_FILE} test_main.py

install:
	@echo "Installing dependencies..."
	@uv sync
	@echo "Installing playwright and chromium headless..."
	@uv run --env-file ${ENV_FILE} playwright install --with-deps --only-shell chromium

clean:
	@echo "Cleaning up..."
	@uv run --env-file ${ENV_FILE} playwright uninstall all 
	@uv run --env-file ${ENV_FILE} task.py --clean
	@rm -rf  ./.venv

clean_task:
	@echo "Cleaning up cron job..."
	@uv run --env-file ${ENV_FILE} task.py --clean

clean_browser_state:
	@echo "Cleaning up browser state..."
	@rm -rf ${PWD}/browser_state.json

task:
	@echo "Creating cron job..."
	@uv run --env-file ${ENV_FILE} task.py --create


.PHONY: test, install, clean, task, clean_browser_state, clean_task
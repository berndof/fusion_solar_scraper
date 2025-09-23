ENV_FILE := ${PWD}/.env

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
	@rm -rf ${PWD}/browser_state.json

clean_task:
	@echo "Cleaning up cron job..."
	@uv run --env-file ${ENV_FILE} task.py --clean

task:
	@echo "Creating cron job..."
	@uv run --env-file ${ENV_FILE} task.py --create

.PHONY: install, clean, task, clean_task
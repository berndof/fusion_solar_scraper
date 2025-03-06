ENV_FILE := ${PWD}/.env


test:
	@echo "Running tests..."
	uv run --env-file ${ENV_FILE} test_main.py

install:
	@echo "Running setup..."
	uv sync
	uv run --env-file ${ENV_FILE} playwright install --with-deps --only-shell chromium

clean:
	@echo "Cleaning up..."
	uv run --env-file ${ENV_FILE} playwright uninstall all

create_cron:
	@echo "Creating cron job..."
	# Chama taks.py para criar o cronjob

.PHONY: test, setup, clean
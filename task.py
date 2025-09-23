from argparse import ArgumentParser, Namespace


from crontab import CronItem, CronTab
from pathlib import Path
import os
import logging
import argparse


# Obtém o intervalo do ambiente (em minutos). Define um valor padrão caso não esteja definido.
def create_task():
    cron_interval = int(os.getenv("CRON_INTERVAL_MINUTES", 5))

    cron: CronTab = CronTab(user=True)
    job: CronItem = cron.new(
        command=f"/bin/bash {Path.cwd()}/run_scraper.sh",
        comment="fusion_solar_scrapper",
    )

    job.minute.every(cron_interval)  # pyright: ignore[reportAttributeAccessIssue]

    cron.write()


def delete_task():
    cron: CronTab = CronTab(user=True)
    cron.remove_all(comment="fusion_solar_scrapper")
    cron.write()


def main():
    parser: ArgumentParser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--create", action="store_true", help="Cria nova tarefa cron")
    group.add_argument(
        "--clean", action="store_true", help="Remove tarefa cron existente"
    )

    args: Namespace = parser.parse_args()

    if args.create:
        create_task()
    elif args.clean:
        delete_task()


if __name__ == "__main__":
    main()

from crontab import CronTab
from pathlib import Path
import os
import logging
import argparse


logger = logging.getLogger("TASK")

# Obtém o intervalo do ambiente (em minutos). Define um valor padrão caso não esteja definido.
def create_task():
    cron_interval = int(os.getenv("CRON_INTERVAL_MINUTES", 5))

    cron = CronTab(user=True)
    job = cron.new(
        command='uv run --env-file %s main.py' % os.path.join(Path.cwd(), '.env'),
        comment='fusion_solar_scrapper'
    )
    job.minute.every(cron_interval)
    cron.write()
    logger.info("Cron job configurado para rodar a cada %s minuto(s)." %cron_interval)

def delete_task():
    cron = CronTab(user=True)
    cron.remove_all(comment='fusion_solar_scrapper')
    cron.write()
    logger.info("Cron job removido.")


def main():
    parser = argparse.ArgumentParser()
    
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument('--create', action='store_true', help='Cria nova tarefa cron')
    group.add_argument('--clean', action='store_true', help='Remove tarefa cron existente')

    args = parser.parse_args()

    if args.create:
        create_task()
    elif args.clean:
        delete_task()

if __name__ == '__main__':
    main()
from playwright.async_api import async_playwright
from scrapper import FusionScrapper
import asyncio
import json
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.WARNING,  # Nível de log padrão
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(os.getenv("LOG_FILE_PATH"),maxBytes=int((os.getenv("MAX_LOG_SIZE_MB") * 1024 )), backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MAIN")
logger.setLevel(logging.DEBUG)

async def main():
    
    async with async_playwright() as pw:
        scrapper = FusionScrapper(pw)    

        try:
            await scrapper.start()
            data = await scrapper.scrap()
            await send_data_to_zabbix(data)
            
        except Exception as e:
            logger.exception(e)
        # finally:
        # await scrapper.stop()    

async def send_data_to_zabbix(data):
    json_payload = json.dumps(data)
    logger.debug(json_payload)

    cmd = [
        "zabbix_sender",
        "-z", os.getenv("ZABBIX_SERVER"),
        "-s", f"'{os.getenv("ZABBIX_HOST")}'",
        "-k", os.getenv("ZABBIX_DATA_KEY"),
        "-p", os.getenv("ZABBIX_PORT"),
        "-o", f"'{json_payload}'"
    ]
    logger.debug(cmd)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(result)
        raise Exception("Erro ao enviar dados para o zabbix")

    logger.info(result.stdout)
    logger.info("Dados enviados com sucesso")

if __name__ == "__main__":
    
    cron_interval = int(os.getenv("CRON_INTERVAL_MINUTES", 5))
    # Define o timeout como (intervalo em segundos - margem de 10 segundos)
    timeout_value = (cron_interval * 60) - 10

    try:
        asyncio.run(asyncio.wait_for(main(), timeout=timeout_value))
    except asyncio.TimeoutError:
        logging.error("Tempo máximo de execução excedido. Script finalizado para evitar sobreposição.")


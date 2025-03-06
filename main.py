from playwright.async_api import async_playwright
from scrapper import FusionScrapper
import asyncio
import json
import os
import subprocess
import logging
from pathlib import Path


#TEMPORARIO
logging.basicConfig(
    level=logging.DEBUG,  # Nível de log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato da mensagem
    handlers=[
        logging.FileHandler(Path.cwd() / "log.txt"),  # Salva em um arquivo
        logging.StreamHandler()  # Exibe no terminal
    ]
)
logger = logging.getLogger("MAIN")

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
        "-o", f"'{json_payload}"
    ]
    logger.debug(cmd)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(result)
        raise Exception("Erro ao enviar dados para o zabbix")

    logger.info(result.stdout)
    logger.info("Dados enviados com sucesso")

if __name__ == "__main__":
    logger.debug("Hello")
    asyncio.run(main())

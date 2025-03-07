from playwright.async_api import async_playwright
from scraper import Scraper
import asyncio
import os
import logging
from logging.handlers import RotatingFileHandler
from zabbix_utils import AsyncSender, ItemValue

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
        scrapper = Scraper(pw)    

        try:
            await scrapper.start()
            data = await scrapper.scrap()
            await send_data_to_zabbix(data)
            
        except Exception as e:
            logger.exception(e)
        finally:
            await scrapper.stop()    

async def send_data_to_zabbix(data):
    host = os.getenv("ZABBIX_HOST")  # Nome do host no Zabbix

    items = [
        ItemValue(host, f"{key}", value)
        for key, value in data.items()
        if value is not None  # Evita enviar dados nulos
    ]

    sender = AsyncSender(server=os.getenv("ZABBIX_SERVER"), port=int(os.getenv("ZABBIX_PORT", 10051)))

    try:
        response = await sender.send(items)
        logger.info(f"Zabbix response: {response}")
    except Exception as e:
        logger.error(f"Erro ao enviar dados para o Zabbix: {e}")

if __name__ == "__main__":
        
    cron_interval = int(os.getenv("CRON_INTERVAL_MINUTES", 5))
    # Define o timeout como (intervalo em segundos - margem de 10 segundos)
    timeout_value = (cron_interval * 60) - 10

    try:
        asyncio.run(asyncio.wait_for(main(), timeout=timeout_value))
    except asyncio.TimeoutError:
        logging.error("Tempo máximo de execução excedido. Script finalizado para evitar sobreposição.")


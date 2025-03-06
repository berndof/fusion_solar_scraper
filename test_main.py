import unittest
from unittest.mock import MagicMock, patch
import asyncio
import logging
from pathlib import Path
from main import main, send_data_to_zabbix

logging.basicConfig(
    level=logging.DEBUG,  # Nível de log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato da mensagem
    handlers=[
        logging.FileHandler(Path.cwd() / "log.txt"),  # Salva em um arquivo
        logging.StreamHandler()  # Exibe no terminal
    ]
)
logger = logging.getLogger("TESTE")


class TestMain(unittest.TestCase):
    
    @patch('main.send_data_to_zabbix')
    def test_main(self, mock_send_data_to_zabbix):
        mock_send_data_to_zabbix.side_effect = self.log_data
        asyncio.run(main())
        mock_send_data_to_zabbix.assert_called_once()


    def log_data(self, data):
        logger.debug(f"Mock: send_data_to_zabbix recebeu {data}")


if __name__ == "__main__":
    unittest.main()
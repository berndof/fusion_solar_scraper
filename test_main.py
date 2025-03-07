import unittest
from unittest.mock import patch
import asyncio
import logging
from main import main

logger = logging.getLogger("TESTE")
logger.setLevel(logging.DEBUG)



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
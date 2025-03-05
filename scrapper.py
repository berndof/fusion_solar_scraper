import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# LOGIN SELECTORS
USERNAME_INPUT_SELECTOR = "#username > input"  # ID + tag
PASSWORD_INPUT_SELECTOR = "#password > input"  # ID + tag
LOGGIN_BUTTON_SELECTOR = "#submitDataverify"  # ID
NEED_CAPTCHA_SELECTOR = "#verificationImg"  # ID

# DATA SELECTORS
NAME_CONTAINER_SELECTOR = ".nco-monitor-header-name-container .ant-typography"  # CSS
NAME_ATTR = "title"

POTENCIA_ATIVA_FATHER_SELECTOR = "span.name:text('Potência ativa')"
POTENCIA_ATIVA_CHILD_SELECTOR = ".nco-monitor-kpi-item"
POTENCIA_ATIVA_VALUE_ATTR = ".value"


class FusionScrapper:
    def __init__(self, pw):
        self.pw = pw
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        # Verirficar se existe estado de navegador salvo
        self.browser = await self.pw.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        try:
            await self.inject_context_scenario()
        except Exception as e:
            await self.create_context_scenario()
            logger.exception(f" exceção !!!! {e}")

    async def check_login(self):
        # Aguarda a validação do login
        try:
            await self.page.wait_for_selector(
                'span[title="%s"]' % os.getenv("FUSIONSOLAR_USERNAME")
            )
        except Exception as e:
            logger.exception(f"Erro ao aguardar o elemento de validacao do login {e}")
            raise e

    async def inject_context_scenario(self):
        # injeta o estado
        logging.debug("inject_context_scenario")
        await self.context.close()
        self.context = await self.browser.new_context(
            storage_state="browser_state.json"
        )
        self.page = await self.context.new_page()

        # vai para a página de monitoramento
        await self.page.goto(os.getenv("MONITOR_PAGE_URL"))

        await self.check_login()

    async def create_context_scenario(self):
        logging.debug("create_context_scenario")

        # vai para a página de login
        await self.page.goto(os.getenv("LOGIN_PAGE_URL"))

        # aguarda os campos do formulário
        username_input_element = await self.page.wait_for_selector(
            USERNAME_INPUT_SELECTOR
        )
        password_input_element = await self.page.wait_for_selector(
            PASSWORD_INPUT_SELECTOR
        )
        login_button_element = await self.page.wait_for_selector(LOGGIN_BUTTON_SELECTOR)

        # Preenche os campos e loga
        await username_input_element.fill(os.getenv("FUSIONSOLAR_USERNAME"))
        await password_input_element.fill(os.getenv("FUSIONSOLAR_PASSWORD"))
        await login_button_element.click()

        # Aguarda a validação do login
        await self.check_login()

        logging.info("Logado com sucesso")

        # vai para a página de monitoramento
        await self.page.goto(os.getenv("MONITOR_PAGE_URL"))

        # Salva o estado do navegador
        await self.page.context.storage_state(path="browser_state.json")

    async def scrap(self):
        data = {
            "nome_usina": await self.get_nome_usina(),
            "data_da_coleta": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "potencia_ativa": await self.get_potencia_ativa(),
        }
        return data

    async def get_nome_usina(self):
        try:
            name_container = await self.page.wait_for_selector(NAME_CONTAINER_SELECTOR)
            return await name_container.get_attribute(NAME_ATTR)
        except Exception as e:
            raise e

    async def get_potencia_ativa(self):
        try:  # Procura o elemento da potencia ativa
            father_element = await self.page.wait_for_selector(
                POTENCIA_ATIVA_FATHER_SELECTOR
            )

            child = await father_element.evaluate_handle(
                f"el => el.closest('{POTENCIA_ATIVA_CHILD_SELECTOR}')"
            )
            value = await child.query_selector(POTENCIA_ATIVA_VALUE_ATTR)
            return await value.inner_text()
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar o valor da potencia ativa",
            )
            raise e

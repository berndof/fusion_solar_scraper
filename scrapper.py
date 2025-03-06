import os
from datetime import datetime
import base64
import logging 

logger = logging.getLogger("SCRAPER")


# LOGIN SELECTORS
USERNAME_INPUT_SELECTOR = "#username > input"  # ID + tag
PASSWORD_INPUT_SELECTOR = "#password > input"  # ID + tag
LOGGIN_BUTTON_SELECTOR = "#submitDataverify"  # ID
CAPTCHA_IMAGE_SELECTOR = "#verificationImg"  # ID
CAPTCHA_INPUT_SELECTOR = "#verification input"

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
        #inicia um navegador com o contexto limpo
        logger.debug("Launching browser...")
        self.browser = await self.pw.chromium.launch(headless=True)
        self.context = await self.browser.new_context()

        try: #tenta injetar o estado do navegador salvo no ultimo login
            await self.inject_context_scenario()

        except Exception as e:
            await self.create_context_scenario()
            logger.exception(f" exceção !!!! {e}")

    async def check_login(self):
        """Verifica se o login foi realizado
        """
        try: #tenta achar o nome do usuário na página
            #await self.page.screenshot(path="debug.png", full_page=True)
            await self.page.wait_for_selector(
                'span[title="%s"]' % os.getenv("FUSIONSOLAR_USERNAME")
            )
            logger.info("Logado no sistema")
        except Exception as e:
            logger.exception(f"Erro ao aguardar o elemento de validacao do login {e}")
            raise e

    async def inject_context_scenario(self):

        #encerra e recria o contexto 
        await self.context.close()
        self.context = await self.browser.new_context(
            storage_state="browser_state.json"
        )
        logger.debug("Contexto injetado com sucesso")

        #cria nova página e navega para a página de monitoramento
        self.page = await self.context.new_page()
        await self.page.goto(os.getenv("MONITOR_PAGE_URL"))

        await self.check_login()
        logger.debug("Valid context")

    async def create_context_scenario(self):
        logger.debug("Creating new context")

        #inicia um novo contexto e vai para a página de login
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.goto(os.getenv("LOGIN_PAGE_URL"))


        #verifica campo de captcha
        try:
            captcha_element = await self.page.wait_for_selector(CAPTCHA_IMAGE_SELECTOR)
            await self.resolve_captcha(captcha_element) 
        except Exception:
            await self.make_login()
            await self.check_login()

        # vai para a página de monitoramento
        await self.page.goto(os.getenv("MONITOR_PAGE_URL"))
        # Salva o estado do navegador
        await self.page.context.storage_state(path="browser_state.json")
        logger.debug("Contexto criado com sucesso")
        
        return 

    async def make_login(self):       

        # aguarda os campos do formulário
        username_input_element = await self.page.wait_for_selector(
            USERNAME_INPUT_SELECTOR
        )
        password_input_element = await self.page.wait_for_selector(
            PASSWORD_INPUT_SELECTOR
        )
        login_button_element = await self.page.wait_for_selector(LOGGIN_BUTTON_SELECTOR)

        # Preenche os campos
        await username_input_element.fill(os.getenv("FUSIONSOLAR_USERNAME"))
        await password_input_element.fill(os.getenv("FUSIONSOLAR_PASSWORD"))

        await login_button_element.click()

        logger.info("Login form filled with success")

    async def resolve_captcha(self, captcha_element):
        while True:
            try:
                img_src = await captcha_element.get_attribute("src")

                if img_src.startswith("data:image"):
                    base64_data = img_src.split(",")[1]
                    with open("captcha.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                    logger.info("Imagem captch salva com sucesso")

                    code = input("Digite o codigo captch: ")
                await self.page.locator(CAPTCHA_INPUT_SELECTOR).press_sequentially(code)
                await self.page.make_login()

            except Exception as e:
                raise e

            # verifica se o captcha foi resolvido
            try: 
                self.check_login()
                break
            except Exception:
                continue
        return 

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

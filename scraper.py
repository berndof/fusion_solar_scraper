import logging
import os
import base64
import re

from pathlib import Path
from datetime import datetime

logger = logging.getLogger("SCRAPER")
logger.setLevel(logging.DEBUG)

USERNAME_INPUT_SELECTOR = "#username > input"
PASSWORD_INPUT_SELECTOR = "#password > input"
LOGGIN_BUTTON_SELECTOR = "#submitDataverify"
CAPTCHA_IMAGE_SELECTOR = "#verificationImg"
CAPTCHA_INPUT_SELECTOR = "#verification input"
NAME_CONTAINER_SELECTOR = ".nco-monitor-header-name-container .ant-typography"  # CSS
NAME_ATTR = "title"

POTENCIA_ATIVA_FATHER_SELECTOR = "span.name:text('Potência ativa')"
POTENCIA_ATIVA_CHILD_SELECTOR = ".nco-monitor-kpi-item"
POTENCIA_ATIVA_VALUE_ATTR = ".value"

POTENCIA_REATIVA_FATHER_SELECTOR = "span.name:text('Potência reativa de saída')"
POTENCIA_REATIVA_CHILD_SELECTOR = ".nco-monitor-kpi-item"
POTENCIA_REATIVA_VALUE_ATTR = ".value"

RENDIMENTO_HOJE_FATHER_SELECTOR = "span.name:text('Rendimento hoje')"
RENDIMENTO_HOJE_CHILD_SELECTOR = ".nco-monitor-kpi-item"
RENDIMENTO_HOJE_VALUE_ATTR = ".value"

RENDIMENTO_TOTAL_FATHER_SELECTOR = "span.name:text('Rendimento total')"
RENDIMENTO_TOTAL_CHILD_SELECTOR = ".nco-monitor-kpi-item"
RENDIMENTO_TOTAL_VALUE_ATTR = ".value"

ENDERECO_SELECTOR = 'div.nco-monitor-station-detail-content:has(div.nco-monitor-station-detail-label-container span:has-text("Endereço da instalação")) div.nco-monitor-station-detail-value-container span'

CAPACIDADE_TOTAL_SELECTOR = 'div.nco-monitor-station-detail-content:has(div.nco-monitor-station-detail-label-container span:has-text("Capacidade total da string")) div.nco-monitor-station-detail-value-container span'

DATA_CONEXAO_SELECTOR = 'div.nco-monitor-station-detail-content:has(div.nco-monitor-station-detail-label-container span:has-text("Data da conexão à rede")) div.nco-monitor-station-detail-value-container span'

SOCIAL_VALUES_SELECTOR='div.nco-monitor-social-contribution-inner div.nco-counter-value .counter-value-main-value .value span'

class Scraper:
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

        #tenta o cenário de injeção de cokies
        try:
            await self.inject_context_scenario()

        except FileNotFoundError:
            await self.create_context_scenario()
        except TimeoutError:
            await self.create_context_scenario()
    
        except Exception as e:
            logger.exception(f" exceção nova !!!! {e}")

        return 

    async def validate_login(self):
        try: #tenta achar o nome do usuário na página
            if os.getenv("SCREENSHOT_DEBUG") == "true":
                await self.page.screenshot(path="screenshots/debug_login.png", full_page=True)
                
            await self.page.wait_for_selector(
                'span[title="%s"]' % os.getenv("FUSIONSOLAR_USERNAME"), timeout=30000
            )
            logger.info("Logado no sistema")
        except Exception as e:
            logging.exception(e)
            raise TimeoutError

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
        
        await self.validate_login()
        logger.debug("Valid context")

    async def create_context_scenario(self):
        logger.debug("Creating new context")

        #inicia um novo contexto e vai para a página de login
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.goto(os.getenv("LOGIN_PAGE_URL"))

        try:
            await self.do_login()
        except Exception:
            captcha_element = await self.page.wait_for_selector(CAPTCHA_IMAGE_SELECTOR)
            if captcha_element: 
                await self.resolve_captcha(captcha_element) 

        await self.validate_login()
        await self.page.goto(os.getenv("MONITOR_PAGE_URL"))

        # Salva o estado do navegador
        await self.page.context.storage_state(path=os.path.join(Path.cwd(), "browser_state.json"))
        logger.debug("Contexto criado com sucesso")

    async def do_login(self):       

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

        await self.validate_login()

        return

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
                await self.page.do_login()

            except Exception as e:
                raise e

            # verifica se o captcha foi resolvido
            try: 
                self.check_login()
                break
            except Exception:
                continue
        return 

    async def stop(self):
        await self.context.close()
        await self.browser.close()
        logger.info("Goodbye...")

    async def scrap(self):
        try:
            data = {
                #"nome_usina": await self.get_nome_usina(), #
                #"endereco": await self.get_endereco(), #
                #"data_conexao": await self.get_data_conexao(), #
                #"capacidade_total": clean_value(await self.get_capacidade_total()), #
                "data_da_coleta": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), #
                "potencia_ativa": clean_value(await self.get_potencia_ativa()), #
                "potencia_reativa_saida": clean_value(await self.get_potencia_reativa_saida()), #
                "rendimento_hoje": await self.get_rendimento_hoje(),
                "rendimento_total": clean_value(await self.get_rendimento_total()),
            }

            social_data = await self.get_social_data()
            for key, value in social_data.items():
                data[key] = clean_value(value)

            alarm_data = await self.get_alarms_data()
            for key, value in alarm_data.items():
                data[f"alarme_{key}"] = int(value)

            logger.info("SCRAPED DATA = %s", data)
            return data

        except Exception as e:
            raise e

    async def get_nome_usina(self):
        name_container = await self.page.wait_for_selector(NAME_CONTAINER_SELECTOR)
        return await name_container.get_attribute(NAME_ATTR)

    async def get_endereco(self):
        try:  # Procura o elemento da potencia ativa
            element = await self.page.wait_for_selector(
                ENDERECO_SELECTOR
            )
            value = await element.inner_text()
            return value
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar o endereço da usina",
            )
            raise e

    async def get_data_conexao(self):
        try:  # Procura o elemento da potencia ativa
            element = await self.page.wait_for_selector(
                DATA_CONEXAO_SELECTOR
            )
            value = await element.inner_text()
            return value
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar a data de conexão",
            )
            raise e

    async def get_capacidade_total(self):
        try:  # Procura o elemento da potencia ativa
            element = await self.page.wait_for_selector(
                CAPACIDADE_TOTAL_SELECTOR
            )
            value = await element.inner_text()
            return value
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar o endereço da usina",
            )
            raise e

    async def get_potencia_ativa(self):
        try:  # Procura o elemento da potencia ativa
            father_element = await self.page.wait_for_selector(
                POTENCIA_ATIVA_FATHER_SELECTOR
            )

            child = await father_element.evaluate_handle(
                f"el => el.closest('{POTENCIA_ATIVA_CHILD_SELECTOR}')"
            )
            value_element = await child.query_selector(POTENCIA_ATIVA_VALUE_ATTR)
            value = await value_element.inner_text()
            return value
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar o valor da potencia ativa",
            )
            raise e

    async def get_potencia_reativa_saida(self):
        try:  # Procura o elemento da potencia ativa
            father_element = await self.page.wait_for_selector(
                POTENCIA_REATIVA_FATHER_SELECTOR
            )

            child = await father_element.evaluate_handle(
                f"el => el.closest('{POTENCIA_REATIVA_CHILD_SELECTOR}')"
            )
            value_element = await child.query_selector(POTENCIA_REATIVA_VALUE_ATTR)
            value = await value_element.inner_text()
            return value
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar o valor da potencia ativa",
            )
            raise e

    async def get_rendimento_hoje(self): 
        try:  # Procura o elemento da potencia ativa
            father_element = await self.page.wait_for_selector(
                RENDIMENTO_HOJE_FATHER_SELECTOR
            )

            child = await father_element.evaluate_handle(
                f"el => el.closest('{RENDIMENTO_HOJE_CHILD_SELECTOR}')"
            )
            value_element = await child.query_selector(RENDIMENTO_HOJE_VALUE_ATTR)
            unit_element = await child.query_selector(".unit")

            raw_value = await value_element.inner_text()
            unit = await unit_element.inner_text() if unit_element else "kWh"  # Padrão kWh

            value = clean_value(raw_value)  # Usa sua função para converter para float

            # Se a unidade for MWh, converter para kWh
            if unit.strip() == "MWh":
                value *= 1000

            if unit.strip() == "kWh":
                value *= 1000
            elif unit == "MWh":
                value *= 1_000_000  # MWh → Wh

            return value
                
        except Exception as e:
            logger.exception(e)
            logger.warning(
                "Nao consegui encontrar o valor da potencia ativa",
            )
            raise e
        

    async def get_rendimento_total(self):
            try:  # Procura o elemento da potencia ativa
                father_element = await self.page.wait_for_selector(
                    RENDIMENTO_TOTAL_FATHER_SELECTOR
                )

                child = await father_element.evaluate_handle(
                    f"el => el.closest('{RENDIMENTO_TOTAL_CHILD_SELECTOR}')"
                )
                value_element = await child.query_selector(RENDIMENTO_TOTAL_VALUE_ATTR)
                value = await value_element.inner_text()
                return value
            except Exception as e:
                logger.exception(e)
                logger.warning(
                    "Nao consegui encontrar o valor da potencia ativa",
                )
                raise e

    async def get_social_data(self):
        contributions = {}
        # Seleciona cada container individual de contribuição
        containers = self.page.locator("div.nco-monitor-social-contribution-inner div.nco-counter-value")
        count = await containers.count()
        # Mapeamento entre os títulos apresentados na página e suas chaves personalizadas
        mapping = {
            "Carvão padrão poupado": "carvao_poupado",
            "CO₂ evitado": "co2_evitado",
            "Árvores equivalentes plantadas": "arvores_plantadas"
        }
        for i in range(count):
            container = containers.nth(i)
            title = (await container.locator(".counter-value-main-title").text_content()).strip()
            value = (await container.locator(".counter-value-main-value .value span").text_content()).strip()
            # Se o título estiver no mapeamento, salva com a chave definida
            if title in mapping:
                contributions[mapping[title]] = value
        return contributions

    async def get_alarms_data(self):
        """Extrai os alarmes e os mapeia para chaves personalizadas."""
        alarms = {}
        # Dicionário de mapeamento: mapeia o título do alarme para a chave que você deseja usar
        mapping = {
            "Sério": "serio",
            "Importante": "importante",
            "Secundário": "secundario",
            "Advert.": "advertencia"
        }
        
        # Seleciona todos os containers de alarme
        alarm_containers = self.page.locator("div.alarm-container")
        count = await alarm_containers.count()
        
        for i in range(count):
            container = alarm_containers.nth(i)
            # O primeiro span dentro de .alarm-info contém o tipo (título) do alarme
            tipo = (await container.locator("div.alarm-info span:nth-of-type(1)").text_content()).strip()
            # O span com a classe alarm-info-value contém o valor
            valor = (await container.locator("div.alarm-info span.alarm-info-value").text_content()).strip()
            # Usa o mapping para definir a chave ou mantém o próprio tipo se não existir no mapping
            chave = mapping.get(tipo, tipo)
            alarms[chave] = valor
        
        return alarms

def clean_value(value):
    """Remove unidades de medida e formata o número corretamente."""
    if value is None:
        return None

    # Remove espaços extras e caracteres não numéricos, exceto ponto e vírgula
    value = value.strip().replace(",", ".")

    # Extrai apenas números (inteiros ou decimais)
    match = re.search(r"[-+]?\d*\.?\d+", value)
    
    if match:
        return float(match.group())  # Retorna como número (float)
    
    return value  # Se não encontrar número, retorna original
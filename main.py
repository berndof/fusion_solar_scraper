from zabbix_utils.types import TrapperResponse


from ast import pattern
from csv import Error
from playwright.async_api._generated import (
    APIResponse,
    Browser,
    BrowserContext,
    Page,
    Response,
)
from playwright.async_api import async_playwright
import asyncio
import os
from typing import Any
import json
from datetime import datetime, timezone
from zabbix_utils import AsyncSender, ItemValue


URL = "https://la5.fusionsolar.huawei.com/"
USERNAME: str | None = os.environ.get("USERNAME")
PASSWORD: str | None = os.environ.get("PASSWORD")
ENDPOINTS: dict[str, str] = {
    "social": "https://la5.fusionsolar.huawei.com/rest/pvms/web/station/v1/station/social-contribution?dn={dn}&clientTime={ts}&timeZone=-3&_={ts}",
    "alarms": "https://la5.fusionsolar.huawei.com/rest/pvms/fm/v1/statistic?stationDn={dn}&_={ts}",
    "stats": "https://la5.fusionsolar.huawei.com/rest/pvms/web/business/v1/stationinfo/station-statistical-information?stationDn={dn}&sceneType=2&_={ts}",
    # "session": "https://la5.fusionsolar.huawei.com/rest/dpcloud/auth/v1/is-session-alive",
}


async def collect_for_station(page: Page, station_dn: str) -> dict[str, Any]:
    ts: int = int(datetime.now(timezone.utc).timestamp() * 1000)
    results: dict[str, Any] = {}

    for key, url_template in ENDPOINTS.items():
        url: str = url_template.format(dn=station_dn, ts=ts)
        try:
            resp: APIResponse = await page.request.get(url)
            if resp.ok:
                try:
                    results[key] = await resp.json()
                except Exception:
                    results[key] = await resp.text()
            else:
                results[key] = {"error": resp.status}
        except Exception as e:
            results[key] = {"error": str(e)}

    return results


async def main():
    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        context: BrowserContext = await browser.new_context()
        page: Page = await context.new_page()

        # TODO maybe
        # try load context, else verify redirect and login

        await page.goto(url=URL)

        # Preencha usuário/senha
        if USERNAME and PASSWORD:
            await page.fill(selector="#username > input", value=USERNAME)
            await page.fill(selector="#password > input", value=PASSWORD)
        await page.click(selector="#submitDataverify")

        stl_timeout = 5000  # ms

        # Aguarda a resposta da lista de estações
        # faz tambem a validação do login mas as vezes da timeout
        # "session": "https://la5.fusionsolar.huawei.com/rest/dpcloud/auth/v1/is-session-alive",
        async with page.expect_response(
            url_or_predicate=lambda response: "/rest/pvms/web/station/v1/station/station-list"
            in response.url,
            timeout=stl_timeout,
        ) as st:
            ...

        station_response: Response = await st.value
        station_json = await station_response.json()
        await context.storage_state(path="states/state.json")

        # adaptar para multiplas estações
        list_items = station_json.get("data", {}).get("list", [])
        if not list_items:
            print("Nenhuma estação encontrada para o usuário.")
            await browser.close()
            return

        station_dn = list_items[0]["dn"]
        raw_data: dict[str, Any] = await collect_for_station(page, station_dn)
        data_to_send: dict[str, Any] = normalize_for_zabbix(raw_data)
        # print(data_to_send)
        # await context.storage_state(path="states/state.json")
        await browser.close()
        # print()
        zabbix_response: TrapperResponse = await send_data_to_zabbix(data=data_to_send)
        # log zabbix response

        return


def normalize_for_zabbix(raw_data: dict[str, Any]) -> dict[str, Any]:
    now: str = datetime.now().strftime(format="%d-%m-%Y %H:%M:%S")

    # --- Social ---
    social = raw_data.get("social", {}).get("data", {})
    carvao_poupado: int = int(social.get("standardCoalSavings", 0))  # kg
    co2_evitado: int = int(social.get("co2Reduction", 0))  # kg
    arvores_plantadas: int = int(social.get("equivalentTreePlanting", 0))

    # --- Stats ---
    stats = raw_data.get("stats", {}).get("data", [])
    potencia_ativa = 0.0  # kW
    potencia_reativa = 0.0  # kvar
    rendimento_hoje = 0.0  # kWh
    rendimento_total = 0.0  # kWh

    for item in stats:
        if item["id"] == 10012:  # Potência ativa
            potencia_ativa = float(item["value"])
        elif item["id"] == 10013:  # Potência reativa
            potencia_reativa = float(item["value"])
        elif item["id"] == 10016:  # Rendimento hoje
            rendimento_hoje = float(item["value"])
        elif item["id"] == 10015:  # Rendimento total
            rendimento_total = float(item["value"])

    # --- Alarms ---
    alarms = raw_data.get("alarms", {}).get("data", [])
    alarme_serio = 0
    alarme_importante = 0
    alarme_secundario = 0
    alarme_advert = 0

    for a in alarms:
        if a["severity"] == "1":
            alarme_serio: int = int(a["value"])
        elif a["severity"] == "2":
            alarme_importante: int = int(a["value"])
        elif a["severity"] == "3":
            alarme_secundario: int = int(a["value"])
        elif a["severity"] == "4":
            alarme_advert: int = int(a["value"])

    return {
        "data_da_coleta": now,
        "potencia_ativa": potencia_ativa,
        "potencia_reativa_saida": potencia_reativa,
        "rendimento_hoje": rendimento_hoje,
        "rendimento_total": rendimento_total,
        "carvao_poupado": carvao_poupado,
        "co2_evitado": co2_evitado,
        "arvores_plantadas": arvores_plantadas,
        "alarme_serio": alarme_serio,
        "alarme_importante": alarme_importante,
        "alarme_secundario": alarme_secundario,
        "alarme_advertencia": alarme_advert,
    }


async def send_data_to_zabbix(data: dict[str, Any]):
    host: str = os.environ.get("ZABBIX_HOST", "")

    items: list[ItemValue] = [
        ItemValue(host=host, key=f"{key}", value=value)
        for key, value in data.items()
        if value
    ]

    sender: AsyncSender = AsyncSender(
        server=os.getenv("ZABBIX_SERVER"), port=int(os.getenv("ZABBIX_PORT", 10051))
    )

    response: TrapperResponse = await sender.send(items)
    return response


if __name__ == "__main__":
    cron_interval = int(os.getenv("INTERVAL_MINUTES", 5))
    # Define o timeout como (intervalo em segundos - margem de 10 segundos)
    timeout_value: int = (cron_interval * 60) - 10

    asyncio.run(main=asyncio.wait_for(fut=main(), timeout=timeout_value))

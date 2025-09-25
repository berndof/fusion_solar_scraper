# Fusion Solar Scraper - Documentação de Instalação e Configuração

## 1. Introdução

O **fusion_solar_scrapper** é um projeto desenvolvido para coletar dados da plataforma Fusion Solar e enviá-los ao Zabbix para monitoramento. Este documento fornece instruções passo a passo para a instalação e configuração do ambiente necessário para a execução do scraper.

## 2. Instalação do Zabbix Sender

O Zabbix Sender é uma ferramenta utilizada para enviar dados personalizados ao servidor Zabbix. Para instalá-lo:

   talvez seja preciso Adicionar o repositório do Zabbix;

   ```bash
   sudo apt install zabbix-sender
   ```

## 3. Instalação do UV Package Manager

O UV é um gerenciador de pacotes e ambientes Python que facilita a gestão de dependências. Para instalá-lo:
https://docs.astral.sh/uv/

## 5. Configuração do Ambiente

1. **Configurar variáveis de ambiente**:

   ```bash
   cp .env.example .env
   nano .env
   ```

   Edite o arquivo `.env` com as configurações específicas do seu ambiente.

2. **Instalar dependências do Python e o navegador para scraping**:

   ```bash
   make install
   ```

   Este comando configura o ambiente virtual e instala as dependencias do python

## 6. Execução e Testes

2. **Configurar execução periódica com o Crontab**:

   Para agendar a execução automática do scraper:

   ```bash
   make task
   ```

   Para verificar se a tarefa foi agendada corretamente:

   ```bash
   crontab -l
   ```

   Você deve ver uma entrada semelhante a:

   ```
   */5 * * * * /bin/bash /caminho/para/fusion_solar_scrapper/run_scraper.sh # fusion_solar_scrapper
   ```

   Os logs das execuções recentes do script estarão em `crontabtask.log`, enquanto os logs do scraper estarão em `collector.log`.

3. **Remover a tarefa agendada**:

   ```bash
   make clean_task
   ```

4. **Executar o scraper manualmente**:

   ```bash
   ./run_scraper.sh
   ```

## 8. Padrão de Resposta

O scraper retorna os dados coletados no seguinte formato JSON:

#TODO corrigir isso aqui com os formatos
```json
{
   "potencia_ativa": 105.377,
   "potencia_reativa_saida": float kvar,
   "rendimento_hoje": 1500000000.0,
   "rendimento_total": 412.91,
   "carvao_poupado": float tonelada
   "co2_evitado": float tonelada
   "arvores_plantadas": 595.0,
   "alarme_serio": 0,
   "alarme_importante": 1,
   "alarme_secundario": 0,
   "alarme_advertencia": 0
}
```

Para integrar esses dados ao Zabbix:

1. **Criar um item no Zabbix** com a chave correspondente ao campo desejado do JSON.
2. **Definir o tipo de informação** conforme o dado (por exemplo, numérico flutuante para valores com casas decimais).

Exemplo de template do host `zbx_usina_template.yaml`




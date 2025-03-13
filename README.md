# Fusion Solar Scraper - Documentação de Instalação e Configuração

## 1. Introdução

O **fusion_solar_scrapper** é um projeto desenvolvido para coletar dados da plataforma Fusion Solar e enviá-los ao Zabbix para monitoramento. Este documento fornece instruções passo a passo para a instalação e configuração do ambiente necessário para a execução do scraper.

## 2. Instalação do Zabbix Sender

O Zabbix Sender é uma ferramenta utilizada para enviar dados personalizados ao servidor Zabbix. Para instalá-lo:

1. **Adicionar o repositório do Zabbix**:

   ```bash
   wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
   sudo dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
   sudo apt update
   ```

2. **Instalar o Zabbix Sender**:

   ```bash
   sudo apt install zabbix-sender
   ```

## 3. Instalação do UV Package Manager

O UV é um gerenciador de pacotes e ambientes Python que facilita a gestão de dependências. Para instalá-lo:
https://docs.astral.sh/uv/

1. **Instalar o `curl`** (se ainda não estiver instalado):

   ```bash
   sudo apt install curl
   ```

2. **Instalar o UV**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Após a instalação, adicione o UV ao seu `PATH` conforme as instruções exibidas no terminal.

## 4. Clonagem do Repositório

Para obter o código-fonte do projeto:

1. **Instalar o Git** (se ainda não estiver instalado):

   ```bash
   sudo apt install git
   ```

2. **Clonar o repositório**:

   ```bash
   git clone https://github.com/berndof/fusion_solar_scrapper.git
   cd fusion_solar_scrapper/
   ```

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

   Este comando configura o ambiente virtual e instala todas as dependências necessárias.

## 6. Execução e Testes

1. **Executar testes iniciais**:

   ```bash
   make test
   ```

   Este comando inicia o scraper e verifica se ele consegue criar uma sessão no Fusion Solar e salvar o estado do navegador. Os logs das execuções são registrados no arquivo `log.txt` no diretório do projeto.

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

   Os logs das execuções recentes do script estarão em `log_sh.txt`, enquanto os logs detalhados do scraper estarão em `log.txt`.

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

```json
{
   "data_da_coleta": "13-03-2025 14:17:13",
   "potencia_ativa": 105.377,
   "potencia_reativa_saida": -0.028,
   "rendimento_hoje": 1500000000.0,
   "rendimento_total": 412.91,
   "carvao_poupado": 366.4,
   "co2_evitado": 435.1,
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




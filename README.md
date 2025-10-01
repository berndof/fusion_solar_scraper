# Fusion Solar Scraper – Guia de Instalação

## 1. Introdução
O **fusion_solar_scrapper** coleta dados da plataforma Fusion Solar e envia ao Zabbix via *zabbix_sender*.

## 2. Dependências

### Zabbix Sender
```bash
sudo apt install zabbix-sender
````

### UV (gerenciador de pacotes Python)

[Instruções oficiais](https://docs.astral.sh/uv/)

## 3. Configuração do Ambiente

1. Criar arquivo de variáveis:

```bash
cp .env.example .env
nano .env
```

2. Instalar dependências e navegador:

```bash
make install
```

## 4. Execução

### Manual

```bash
./run_scraper.sh
```

### Automática (crontab)

Agendar:

```bash
make task
```

Listar tarefas:

```bash
crontab -l
```

Remover agendamento:

```bash
make clean_task
```

Logs ficam em `log/`:

* `crontabtask.log` → execução agendada
* `collector.log` → saída do scraper



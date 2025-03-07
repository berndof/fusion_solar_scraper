
# Dependencias

zabbix-sender irá enviar os dados para o zabbix, talvez seja necessário adicionar os repositórios do zabbix

https://www.zabbix.com/download?zabbix=7.2&os_distribution=ubuntu&os_version=24.04&components=agent&db=&ws=
> usando a versão mais recente atual, talvez o repositório mude

```bash
wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
apt update
apt install zabbix-sender
```

instalar o uv package manager, para gerenciar o ambiente e as dependencias do python
https://github.com/astral-sh/uv
```shell
apt install curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

clonar o repositorio 

```bash
apt install git
git clone https://github.com/berndof/fusion_solar_scrapper.git
cd fusion_solar_scrapper/
```

Configurar o .env

```bash
cp .env.example .env
nano .env
```

instalar dependencias do python e navegador para scrapinh

```bash 
make install
```

nesse momento se rodarmos 
```bash
make test
```

devemos ver os logs do script criando uma sessão no fusion solar e salvando a sessão do navegador para injetar posteriormente 

```bash
Running tests...  
2025-03-07 11:20:55,914 - SCRAPER - DEBUG - Launching browser...  
2025-03-07 11:20:56,267 - SCRAPER - DEBUG - Creating new context  
2025-03-07 11:21:26,835 - SCRAPER - INFO - Login form filled with success  
2025-03-07 11:21:28,665 - SCRAPER - INFO - Logado no sistema  
2025-03-07 11:21:28,697 - SCRAPER - DEBUG - Contexto criado com sucesso
```

e ao final a saída dos dados coletados. 

tudo isso fica registrado no arquivo `log.txt`no mesmo diretório do projeto

para rodar como um crontab 
```bash
make task
```

para verificar se a task foi criada corretamente 

``` bash
crontab -l
```

deve existir uma tarefa que chama o script `run_scraper.sh`  

```
*/5 * * * * /bin/bash /root/fusion_solar_scrapper/run_scraper.sh # fusion_solar_scrapper
```

o run_scraper.sh cria  log_sh.txt que registra as execuções recentes do script 

rodando 
```bash
make clean_task
```

removemos a tarefa 


adicionar item no zabbix

![[Pasted image 20250228202006.png]]

zabbix_sender -v -z localhost -s "Usina SCC" -k "fusion_solar_data" -o "dados"
![[Pasted image 20250228201904.png]]

#TODO mapear o json path

## Script python

## Resposta Json

data e hora da coleta -x
nome da instalação -x

endereço da instalação
energia nominal do inversor
data de conexão a rede 
capacidade total

potencia ativa - x 
potencia reativa de saida
rendimento hoje
rendimento total
Carvão poupado 
co2evitado 
tree_equivalent

alarms
Danger
Warning
Secundary
Advert

## Dependencias do playwright 

uv run palywright install chromium / install-deps


## TODO 
Response from "10.14.1.12:10051": "processed: 0; failed: 1; total: 1; s  
econds spent: 0.000057"


evaluate response from zabbix
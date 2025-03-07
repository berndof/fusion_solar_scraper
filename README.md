## Como rodar o scraper

## Instalar o uv package manager 
https://docs.astral.sh/uv/getting-started/installation/


```bash
sudo apt install make
```

## Comando install
O comando install é responsável por instalar as dependências necessárias para o projeto. Ele executa as seguintes ações:

Instala as dependências do projeto usando o comando uv sync.
Instala o Playwright e o Chromium headless usando o comando playwright install --with-deps --only-shell chromium.
Ordem de uso: O comando install deve ser executado primeiro para garantir que todas as dependências necessárias estejam instaladas.

## Comando task
O comando task é responsável por criar um cron job para executar o projeto. Ele executa as seguintes ações:

Cria um cron job usando o comando task --create.

O comando task é opcional e pode ser executado após o comando install. 
Se você não precisar de um cron job, pode pular este comando.

## Comando test
O comando test é responsável por executar os testes do projeto. Ele executa as seguintes ações:

Executa os testes do projeto usando o comando uv run --env-file ${ENV_FILE} test_main.py.

O comando test pode ser executado após o comando install e task (se aplicável).

## Comando clean
O comando clean é responsável por limpar o projeto. Ele executa as seguintes ações:

Desinstala o Playwright e o Chromium headless usando o comando playwright uninstall all.
Limpa o projeto usando o comando task --clean.

O comando clean pode ser executado a qualquer momento para limpar o projeto.


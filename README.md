sudo apt install make



run 
uv sync
uv run --env-file .env playwright install --with-deps --only-shell chromium

## service 
sudo nano /etc/systemd/system/huawei-scraper.service
└─[$] <git:(main*)> sudo systemctl daemon-reload

Restart=always → Garante que o serviço sempre reinicia quando termina.
🔹 RestartSec=300 → Espera 5 minutos antes de reiniciar.
🔹 RuntimeMaxSec=290 → Mata o processo se ele rodar por mais de 4 minutos e 50 segundos (para evitar sobreposição).


https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html#id-1.7
https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html

 sudo cp fusion_scrapper.service /etc/systemd/system/fusion_scrapper.service && sudo systemctl daemon-reload && sudo systemctl start fusion_scrapper.service
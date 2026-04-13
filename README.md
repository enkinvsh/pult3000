# Pult3000

Telegram-пульт для YouTube Music на Mac.

## Требования

- macOS с Chrome
- Python 3.13+
- Telegram бот (через @BotFather)
- Прокси (если из РФ)

## Установка

```bash
git clone https://github.com/enkinvsh/pult3000.git
cd pult3000
cp .env.example .env
# Заполни .env (BOT_TOKEN, ADMIN_ID, PROXY_URL)

python3.13 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/playwright install chromium

# Автозапуск
bash deploy/install.sh
```

## .env

```
BOT_TOKEN=123456:ABC...
ADMIN_ID=123456789
PROXY_URL=socks5://127.0.0.1:7890
```

## Клавиатура

```
⏮  ⏯  ⏭     — prev/play-pause/next
🔀  ❤️  📻     — shuffle/like/radio (плейлист артиста)
15% 25% 50% 75% 100%  — громкость
```

## Команды

- `/start` — показать клавиатуру
- Текст — поиск и воспроизведение

## Логи

```bash
tail -f logs/bot.error.log
```

## Управление

```bash
# Стоп
launchctl unload ~/Library/LaunchAgents/com.pult3000.plist

# Старт
launchctl load ~/Library/LaunchAgents/com.pult3000.plist
```

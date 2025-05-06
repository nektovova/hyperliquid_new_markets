import requests
import json
import time
import os
from datetime import datetime
from telegram import Bot

# Параметры для Telegram
TELEGRAM_BOT_TOKEN = '6886610423:AAGI6rmwCkk5T9wJ2ix1oiXzbW905N65gSk'
TELEGRAM_CHANNEL_ID = '-1002294884838'

# Путь к файлу для сохранения списка рынков
MARKETS_FILE = 'markets.json'

# URL и параметры запроса к API Hyperliquid
API_URL = 'https://api.hyperliquid.xyz/info'
HEADERS = {'Content-Type': 'application/json'}
PAYLOAD = {'type': 'meta'}

def fetch_markets():
    """Запрашивает текущий список рынков с Hyperliquid."""
    try:
        response = requests.post(API_URL, json=PAYLOAD, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data.get('universe', [])
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при выполнении запроса: {e}')
        return []

def load_saved_markets():
    """Загружает ранее сохраненный список рынков из файла."""
    if os.path.exists(MARKETS_FILE):
        with open(MARKETS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_markets(markets):
    """Сохраняет текущий список рынков в файл."""
    with open(MARKETS_FILE, 'w') as file:
        json.dump(markets, file, indent=4)

def send_telegram_message(message, apikey=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHANNEL_ID):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(apikey,chat_id,message)
    requests.get(url)
def main():
    saved_markets = load_saved_markets()
    saved_market_names = {market['name'] for market in saved_markets}

    while True:
        current_markets = fetch_markets()
        current_market_names = {market['name'] for market in current_markets}

        # Определяем новые рынки
        new_markets = current_market_names - saved_market_names
        if new_markets:
            message = f"Обнаружены новые рынки на Hyperliquid:\n" + "\n".join(f"- {name}" for name in new_markets)
            send_telegram_message(message)
            # Обновляем сохраненный список рынков
            save_markets(current_markets)
            saved_market_names = current_market_names

        # Ждем 60 секунд перед следующим запросом
        time.sleep(60)

if __name__ == '__main__':
    main()

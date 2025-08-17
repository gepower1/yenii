import os
import telebot
from flask import Flask, request
import requests

TOKEN = "7591570412:AAGJ43nkH6ZZikX6VMJGCXVbpyUxyrDb8OA"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# -------------------------
# İlk 500 coin listesi
# -------------------------
def get_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 500, "page": 1}
    response = requests.get(url).json()
    mapping = {}
    for coin in response:
        mapping[coin["symbol"].lower()] = coin["id"]
    return mapping

coin_mapping = get_coin_list()

# -------------------------
# Fiyat alma fonksiyonu
# -------------------------
def get_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url).json()
    return response.get(coin_id, {}).get("usd")

# -------------------------
# Komutlar
# -------------------------
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "👋 Merhaba! Örnek: `/price btc` veya `/price eth` yaz, fiyatını göstereyim.", parse_mode="Markdown")

@bot.message_handler(commands=['price'])
def price_message(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Kullanım: `/price btc`", parse_mode="Markdown")
            return

        symbol = parts[1].lower()
        coin_id = coin_mapping.get(symbol)

        if not coin_id:
            bot.reply_to(message, f"❌ `{symbol}` bulunamadı.", parse_mode="Markdown")
            return

        price = get_price(coin_id)
        if price:
            bot.reply_to(message, f"💰 {symbol.upper()} fiyatı: {price} USD")
        else:
            bot.reply_to(message, f"❌ {symbol.upper()} fiyat bilgisi alınamadı.")
    except Exception as e:
        bot.reply_to(message, f"🚨 Hata: {str(e)}")

# -------------------------
# Webhook
# -------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot çalışıyor 🚀", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

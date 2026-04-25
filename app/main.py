import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Webhook para conectar Telegram con el sistema de recomendación
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return 'OK'
    
    chat_id = data['message']['chat']['id']
    text = data['message']['text']
    
    response = f'Mensaje recibido: {text}'
    
    send_message(chat_id, response)
    
    return 'OK'

# Envío de mensaje por el bot en Telegram
def send_message(chat_id, text):
    URL = f'{BASE_URL}/sendMessage'
    
    payload = {'chat_id': chat_id, 'text': text}
    
    requests.post(URL, json=payload)
    
if __name__== '__main__':
    app.run(port=5000, debug=True)
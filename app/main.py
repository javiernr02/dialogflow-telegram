import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

PROJECT_ID = os.getenv('PROJECT_ID')
SESSION_CLIENT = dialogflow.SessionsClient()

# Webhook para conectar Telegram con Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
        
    if not data or 'message' not in data:
        return 'OK'
    
    chat_id = data['message']['chat']['id']
    text = data['message']['text']
    
    # Conexión con DialogFlow
    result = detect_intent(text, chat_id)
    
    response_text = result.fulfillment_text
    
    # Respuesta en Telegram
    send_message(chat_id, response_text)
        
    return 'OK'

# Envío de mensaje por el bot en Telegram
def send_message(chat_id, text):
    URL = f'{BASE_URL}/sendMessage'
    
    payload = {'chat_id': chat_id, 'text': text}
    
    requests.post(URL, json=payload)
    
def detect_intent(text, session_id):
    session = SESSION_CLIENT.session_path(PROJECT_ID, str(session_id))

    text_input = dialogflow.TextInput(text=text, language_code='es')

    query_input = dialogflow.QueryInput(text=text_input)

    response = SESSION_CLIENT.detect_intent(request={'session': session, 'query_input': query_input})

    return response.query_result

@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    data = request.get_json()
        
    if not data or 'queryResult' not in data:
        return 'OK'
    
    intent = data['queryResult']['intent']['displayName']
    text = data['queryResult'].get('queryText', '')
        
    try:
        if intent == 'Greeting':
            response = 'Hola'
        elif intent == 'Recommend Movie':
            response = 'Te recomiendo películas'
        else:
            response = 'No entiendo tu mensaje'
            
    except Exception:
        response = 'Ha ocurrido un error, inténtalo de nuevo más tarde'
        
    return jsonify({"fulfillmentText": response})
    
    
if __name__== '__main__':
    app.run(port=5000, debug=True)
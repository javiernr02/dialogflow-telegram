import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow
from recommender import movies_by_genre, movies_by_genre_and_year, movies_by_year, movie_info_by_title, is_movie_popular

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

PROJECT_ID = os.getenv('PROJECT_ID')
SESSION_CLIENT = dialogflow.SessionsClient()

user_state = {}

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

# Detecta intents definidos en DialogFlow
def detect_intent(text, session_id):
    session = SESSION_CLIENT.session_path(PROJECT_ID, str(session_id))

    text_input = dialogflow.TextInput(text=text, language_code='es')

    query_input = dialogflow.QueryInput(text=text_input)

    response = SESSION_CLIENT.detect_intent(request={'session': session, 'query_input': query_input})

    return response.query_result

# Webhook para conectar DialogFlow con Flask
@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    data = request.get_json()
    
    chat_id = (
        data.get('originalDetectIntentRequest', {})
        .get('payload', {})
        .get('data', {})
        .get('chat', {})
        .get('id', 'test_user')
    )
        
    if not data or 'queryResult' not in data:
        return 'OK'
    
    intent = data['queryResult']['intent']['displayName']
        
    try:
        if intent in ['Greeting', 'Gratitude']:
            response = 'Hola'
        elif intent == 'Recommend Movie':
            genre = data['queryResult']['parameters'].get('genre')
            
            year = data['queryResult']['parameters'].get('number-integer')
            
            genre_dic = {
                    'Action': 'acción',
                    'Comedy': 'comedia',
                    'Drama': 'drama',
                    'Horror': 'miedo',
                    'Romance': 'romance',
                    'Adventure': 'aventura',
                    'Thriller': 'suspense',
                    'Sci-Fi': 'ciencia ficción',
                    'War': 'guerra',
                    'Western': 'del oeste',
                    'Film-Noir': 'película negra',
                    'Crime': 'crimen',
                    'Fantasy': 'fantasía',
                    'Mystery': 'misterio',
                    'Children': 'niños',
                    'Animation': 'animación',
                    'Documentary': 'documental',
                    'Musical': 'musical',
                    'IMAX': 'IMAX'
                }
            
            genre_text = genre_dic.get(genre, genre)
            
            if genre and year:
                all_movies = movies_by_genre_and_year(genre, year)
                
                if 1919 <= int(year) <= 2018:
                    if all_movies:
                        response = f'🤓 Te recomiendo las siguientes películas de {genre_text} del año {int(year)}:\n\n'
                        response += '\n'.join(all_movies[:10])
                        
                        user_state[chat_id] = {'movies': all_movies, 'index':10}
                    else:
                        response = '😭 No encontré ninguna película con ese criterio'
                else:
                    response = 'Solo tengo conocimientos de películas entre los años 1919 y 2018 incluidos'
            
            elif genre:
                all_movies = movies_by_genre(genre)
                
                if all_movies:
                    response = f'🤓 Te recomiendo las siguientes películas de {genre_text}:\n\n'
                    response += '\n'.join(all_movies[:10])
                    
                    user_state[chat_id] = {'movies': all_movies, 'index':10}
                else:
                    response = '😭 No encontré ninguna película con ese criterio'
                
            elif year:
                if 1919 <= int(year) <= 2018:
                    all_movies = movies_by_year(year)
                    
                    if all_movies:
                        response = f'🤓 Te recomiendo las siguientes películas del año {int(year)}:\n\n'
                        response += '\n'.join(all_movies[:10])
                        
                        user_state[chat_id] = {'movies': all_movies, 'index':10}
                    
                    else:
                        response = '😭 No encontré ninguna película con ese criterio'
                    
                else:
                    response = 'Solo tengo conocimientos de películas entre los años 1919 y 2018 incluidos'
                    
            else:
                response = '🎬 Dime un género o un año o ambas cosas'
                
        elif intent == 'More Movies':
            
            state = user_state.get(chat_id)
            
            if not state:
                response = 'Primero pide recomendaciones'
            
            else:
                movies = state['movies']
                index = state['index']
                
                next_movies = movies[index:index+10]
                
                if next_movies:
                    response = "Aquí tienes más películas:\n\n" + "\n".join(next_movies)
                    user_state[chat_id]['index'] += 10
                else:
                    response = 'No tengo más películas'
                    
        elif intent == 'Movie Info':
            title = data['queryResult']['parameters'].get('any')
            text = data['queryResult']['queryText'].lower()
            
            information = movie_info_by_title(title)
            
            title = information['title']
            year = information['year']
            genres = information['genres']
            rating = information['rating']
            
            if information:
                
                if 'valoracion' in text:
                    if rating:
                        response = f'{title} tiene una valoración media de {rating}/5'
                    else:
                        response = f'{title} no tiene valoraciones'
                        
                elif 'genero' in text or 'categoria' in text or 'tipo' in text or 'clasificacion' in text or 'generos' in text or 'categorias' in text or 'tipos' in text:
                    if genres:
                        response = f'{title} tiene los géneros: {genres}'
                    else:
                        response = f'{title} no tiene géneros'
                    
                else:
                    response = f'La información encontrada para {title} es:\nAño: {year}\nGéneros: {genres}'
                    if rating:
                        response += f'\nMedia de valoraciones: {rating}/5'
                    else:
                        response += '\nSin valoraciones'
            else:
                response = '😭 No encontré esa película'
        
        elif intent == 'Movie Popularity':
            title = data['queryResult']['parameters'].get('any')
            
            result = is_movie_popular(title)
            
            if result:
                response = f'{title} es una película {result}'
            else:
                response = '😭 No encontré esa película'
             
        else:
            response = 'No entiendo tu mensaje'
            
    except Exception:
        response = 'Ha ocurrido un error, inténtalo de nuevo más tarde'
        
    return jsonify({"fulfillmentText": response})
    
    
if __name__== '__main__':
    app.run(port=5000, debug=True)
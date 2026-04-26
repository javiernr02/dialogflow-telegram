import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

movie_stats = ratings.groupby('movieId').agg(avg_rating=('rating', 'mean'),num_ratings=('rating', 'count')).reset_index()

movies_ml = movies.merge(movie_stats, on='movieId', how='left')

movies_ml['avg_rating'] = movies_ml['avg_rating'].fillna(0)
movies_ml['num_ratings'] = movies_ml['num_ratings'].fillna(0)

movies_ml['main_genre'] = movies_ml['genres'].str.split('|').str[0]

movies_ml['popular'] = movies_ml['avg_rating'].apply(lambda x: 1 if x >= 3 else 0)

label_encoder = LabelEncoder()
movies_ml['genre_encoded'] = label_encoder.fit_transform(movies_ml['main_genre'])

# Entreno árbol de decisión
X = movies_ml[['avg_rating', 'num_ratings', 'genre_encoded']]
y = movies_ml['popular']

model_popularity = DecisionTreeClassifier(max_depth=4)
model_popularity.fit(X, y)

# Función principal árbol
def is_movie_popular(title):
    
    movie = movies_ml[movies_ml['title'].str.lower().str.contains(title.lower(), na=False)]

    if movie.empty:
        return None

    row = movie.iloc[0]

    features = [[
        row['avg_rating'],
        row['num_ratings'],
        row['genre_encoded']
    ]]

    prediction = model_popularity.predict(features)[0]
    
    if prediction == 1:
        return 'recomendable'
    else:
        return 'recomendable'

movies['genres_list'] = movies['genres'].str.split('|')

movies['year'] = movies['title'].str.extract(r'\((\d{4})\)')[0].fillna('0').astype(int)

def movies_by_genre(genre):
    movies_filtered = movies[movies['genres_list'].apply(lambda x: genre in x if isinstance(x, list) else False)]
    
    return movies_filtered['title'].tolist()

def movies_by_year(year):
    movies_filtered = movies[movies['year'] == int(year)]
    
    return movies_filtered['title'].tolist()

def movies_by_genre_and_year(genre, year):
    filtered = movies[
        (movies['genres_list'].apply(lambda x: genre in x)) & (movies['year'] == int(year))]
    
    return filtered['title'].tolist()

def movie_info_by_title(title):
    movie =  movies[movies['title'].str.lower().str.contains(title.lower(), na=False)]
    
    if movie.empty:
        return None

    movie = movie.iloc[0]
    
    movie_id = movie['movieId']
    
    movie_ratings = ratings[ratings['movieId'] == movie_id]
    
    if not movie_ratings.empty:
        avg_rating = movie_ratings['rating'].mean()
    else:
        avg_rating = None
    
    return {'title': movie['title'], 'genres': movie['genres'], 'year': movie['year'], 'rating': round(avg_rating, 2) if avg_rating else None}
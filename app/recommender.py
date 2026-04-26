import pandas as pd

movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

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
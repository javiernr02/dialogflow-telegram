import pandas as pd

movies = pd.read_csv('data/movies.csv')

def movies_by_genre(genre, n):
    movies['genres_list'] = movies['genres'].str.split('|')
    movies_filtered = movies[movies['genres_list'].apply(lambda x: genre in x)]
    
    return movies_filtered['title'].head(n).tolist()
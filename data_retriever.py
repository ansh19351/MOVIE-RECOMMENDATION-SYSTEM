import sqlite3
from colorama import Cursor
import pandas as pd




def imdb_link(movie_id):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT imdbId FROM links WHERE movieId = {movie_id}')
    records = cursor.fetchall()
    lst = []
    for row in records:
        lst.append(row)
    movie_link = lst[0][0]
    conn.close()
    return movie_link

def get_ratings(movie_id):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT AVG(rating) FROM ratings GROUP BY movieId HAVING movieId = {movie_id}')
    
    records = cursor.fetchall()
    lst = []
    for row in records:
        lst.append(row)
    return lst[0][0]

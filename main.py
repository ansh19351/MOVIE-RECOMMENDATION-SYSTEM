from unicodedata import decimal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import process
from flask import Flask, redirect, url_for, request,render_template
import data_retriever
import requests
from bs4 import BeautifulSoup
import numpy as np

movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')
links = pd.read_csv('links.csv',converters={'imdbId': str})
final_dataset = ratings.pivot(index='movieId',columns='userId',values='rating')
final_dataset.fillna(0,inplace=True)

compressed_dataset = csr_matrix(final_dataset.values)
final_dataset.reset_index(inplace=True)
model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20)
model.fit(compressed_dataset)



def recommend_movie(desc_list):
  d_list = desc_list.split('$')
  movie_idx = process.extractOne(d_list[0],movies['title'])[2]
  print("Movie Selected: ",movies['title'][movie_idx])
  distances, indices = model.kneighbors(compressed_dataset[movie_idx], n_neighbors=int(d_list[1]))
  indices = indices[0]
  movies_list = []
  for i in indices:
    lst = []
    lst.append(movies['title'][i])
    lst.append(data_retriever.imdb_link(movies['movieId'][i]))
    lst.append(movies['genres'][i])
    lst.append(data_retriever.get_ratings(movies['movieId'][i]))
    movies_list.append(lst)
  idx = 0
  for i in movies_list:
    imdb_link = f"https://www.imdb.com/title/tt{i[1]}"
    r = requests.get(imdb_link)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        image_url = soup.find('div', class_='ipc-poster').img['src']
    except:
        image_url = np.nan
    movies_list[idx].append(image_url)
    movies_list[idx].append(imdb_link)
    idx += 1
  return movies_list





app = Flask(__name__)

@app.route('/home/<data>')
def home(data):
   return render_template('home.html', data=recommend_movie(data))

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.form['mname']
      nbrs = request.form['rel_movies']
      desc_list = f"{user}${nbrs}"
      print(desc_list)
      return redirect(url_for('home',data = desc_list))
   else:
      user = request.args.get('mname')
      nbrs = request.args.get('rel_movies')
      desc_list = f"{user}${nbrs}"
      return redirect(url_for('home',data = desc_list))

if __name__ == '__main__':
   app.run(debug = True)
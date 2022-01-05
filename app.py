from numpy import load
from flask import Flask, request, jsonify, render_template, url_for
import pickle
import bz2
import _pickle as cPickle
import lxml
#from pandas import Series, read_csv
#from joblib import load
import json
import requests
import bs4
from bs4 import BeautifulSoup
app = Flask(__name__)
#rbf_ker_cv = load('rbf_ker_cv.joblib')
#rbf_ker_cv = load('rbf_ker_cv_pick.pbz2', allow_pickle=True)
#rbf_ker_cv_z = load('rbf_ker_cv.npz')
#rbf_ker_cv = rbf_ker_cv_z['a']
#df = read_csv('df.csv')

file = open('movie_titles.pickle','rb')
movie_title = pickle.load(file)
file = open('imdb_links.pickle','rb')
imdb_links = pickle.load(file)

def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = cPickle.load(data)
    return data
rbf_ker_cv = decompress_pickle('rbf_ker_cv_pick.pbz2') 

headers = {
    'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
}
movie_title_enumerated = list(enumerate(movie_title))

def recommendation(title, kernel):
    recomm = []
    for i in range(len(movie_title)):
        if movie_title_enumerated[i][1] == title:
            idx = movie_title_enumerated[i][0]
    #idx = indices[title]
    #print(idx)
    global sim_scores
    sim_scores = list(enumerate(kernel[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]
    for y in movie_indices:
        recomm.append(movie_title[y])
    return movie_indices, recomm

def scrapper(movie):
    liste_image_url_names = []
    #for i in range(len(movie)):
        #liste_image_url_names.append(movie[i])
    list_url_image = []
    for i in movie:
        list_url_image.append(imdb_links[i])
    photos = []
    for i in range(5):
        r = requests.get(list_url_image[i], {'headers':headers})
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        image = soup.find_all('div',
                        {'class':"ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40 ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img"})[-1].extract()
        
        child = 'src'
        for child in image:
            child
        photo = child['src']
        
        photos.append(photo)
    return photos


@app.route("/")
@app.route("/home")
@app.route("/index")

def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST','GET'])
@app.route("/home", methods=['POST','GET'])
@app.route("/index", methods=['POST','GET'])

def my_get():
    if request.method == "POST":
        movie = request.form['nm']
        not_found = 'not_found'
        if movie in movie_title:
            movies = recommendation(movie, rbf_ker_cv)
            imgs = scrapper(movies[0])
            return render_template('recommendation.html' , movie=movies[1], imgs=imgs)
        else:
            return render_template('index.html' , movie=not_found)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)
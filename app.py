import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "artists.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ArtistTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(255), nullable=False)
    track_title = db.Column(db.String(255), nullable=False)
    album_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Track {self.track_title} by {self.artist_name} from album {self.album_name}>"


def get_artist_data(artist_name):
    url = "https://deezerdevs-deezer.p.rapidapi.com/search"
    querystring = {"q": artist_name}

    headers = {
        "x-rapidapi-key": "b1c6e303c5mshd4aa08c367fd6b4p137c7fjsne2d9b745b9bb",
        "x-rapidapi-host": "deezerdevs-deezer.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()


def save_artist_info(artist_name, results):
    for track in results['data']:
        title = track['title']
        artist = track['artist']['name']
        album = track['album']['title']

        new_track = ArtistTrack(artist_name=artist, track_title=title, album_name=album)
        db.session.add(new_track)

    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        artist_name = request.form['artist_name']
        return redirect(url_for('search_artist', artist_name=artist_name))
    return render_template('index.html')


@app.route('/search/<artist_name>', methods=['GET'])
def search_artist(artist_name):
    results = get_artist_data(artist_name)

    if results and 'data' in results and results['data']:
        save_artist_info(artist_name, results)
        return render_template('results.html', artist_name=artist_name, results=results['data'])
    else:
        return f"Brak wyników dla artysty: {artist_name}"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

app = Flask(__name__)
api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модель
class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    genres = relationship("Movie", back_populates="genre")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    # genre = db.relationship("Genre", back_populates="genres")
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


# сериализация
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


# Создаём  экземпляр схемы
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# Создаём  экземпляр схемы
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# Создаём  экземпляр схемы
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# регистрируем класс (CBV) (ресурс) по определенному пути (эндпоинту)
@movie_ns.route('/', methods=['GET'])
class MoviesView(Resource):
    def get(self):
        genre_id = request.args.get('genre_id')
        director_id = request.args.get('director_id')

        if (genre_id is not None) and (director_id is not None):
            all_movies__dir_gen = Movie.query.filter(
                (Movie.genre_id == genre_id), (Movie.director_id == director_id)).all()
            return movies_schema.dump(all_movies__dir_gen), 200

        elif (genre_id is None) and (director_id is not None):
            director_id = request.args.get('director_id')
            all_movies_by_director = Movie.query.filter(Movie.director_id == director_id).all()
            return movies_schema.dump(all_movies_by_director), 200

        elif (genre_id is not None) and (director_id is None):
            genre_id = request.args.get('genre_id')
            all_movies_genre = Movie.query.filter(Movie.genre_id == genre_id).all()
            return movies_schema.dump(all_movies_genre), 200

        else:
            all_movies = Movie.query.all()
            return movies_schema.dump(all_movies), 200


@movie_ns.route('/<int:uid>', methods=['GET'])
class MovieView(Resource):
    def get(self, uid: int):
        try:
            movie = Movie.query.get(uid)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return "", 404


@director_ns.route('/', methods=['GET', 'POST'])
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        if request.method == 'POST':
            req_json = request.json
            new_director = Director(**req_json)
            with db.session.begin():
                db.session.add(new_director)
            return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        try:
            director = Director.query.get(uid)
            return director_schema.dump(director), 200
        except Exception as e:
            return "", 404

    def put(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return "", 404
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route('/', methods=['GET', 'POST'])
class GenresView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        if request.method == 'POST':
            req_json = request.json
            new_genre = Genre(**req_json)
            with db.session.begin():
                db.session.add(new_genre)
            return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        try:
            genre = Genre.query.get(uid)
            return genre_schema.dump(genre), 200
        except Exception as e:
            return "", 404

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return "", 404
        req_json = request.json
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)

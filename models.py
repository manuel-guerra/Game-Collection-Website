from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False)
    dob = db.Column(db.Date, default=None)
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))
    # game_collections = db.relationship('GameCollection', backref='user', lazy=True)

    @property
    def id(self):
        return self.user_id



class Games(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100))
    metacritic_rating = db.Column('MetacriticRating', db.Integer)
    esrb = db.Column(db.String(5))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    developer = db.Column(db.String(100))
    release_date = db.Column(db.Date)
    average_rating = db.Column('AverageRating', db.Float(precision=2))


# class GameCollection(db.Model):
#     collection_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     items = db.relationship('GameCollectionItems', backref='gamecollection', lazy=True)
#
#
#
# class GameCollectionItems(db.Model):
#     collection_items_id = db.Column(db.Integer, primary_key=True)
#     collection_id = db.Column(db.Integer, db.ForeignKey('game_collection.collection_id'), nullable=False)
#     game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
#     status = db.Column(db.String(20))
#     user_rating = db.Column(db.Integer)
#     favorite_games = db.Column(db.Boolean, default=False)
#     total_play_time = db.Column(db.Integer)
import os
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin

from views import views as views_blueprint
from models import db, Users

#Load environment variables from .env
load_dotenv()

# Create the application instance
app = Flask(__name__)

# App Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'views.login'

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

app.register_blueprint(views_blueprint, url_prefix='/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create all the database tables
        app.run(debug=True)

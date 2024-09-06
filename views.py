from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import text

from models import db, Users, Games

views = Blueprint(__name__, 'views')


@views.route('/')
def home():
    return redirect(url_for('views.games'))


@views.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()

        if user:
            if user and user.password == password:
                flash('Logged in successfully.')
                login_user(user, remember=True)
                return redirect(url_for('views.profile'))
            else:
                flash('Incorrect password, try again.')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)


@views.route('/logout/')
@login_required
def logout():
    user = current_user.first_name
    logout_user()
    flash(f'{user} logged out successfully', category='success')
    return redirect(url_for('views.login'))


@views.route('/sign-up/', methods=['POST', 'GET'])
def sign_up():
    if current_user.is_authenticated:
        flash('You are already logged in. ')
        return redirect(url_for('views.profile'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        dob = request.form.get('dob')

        user = Users.query.filter_by(email=email).first()

        # category will be used when bootstrap is added.
        if user:
            flash('Email already exists.', category='error')
        elif len(email) > 40:
            flash('Email must be at least 40 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) > 50:
            flash('Password at most can be 50 characters', category='error')
        else:
            # if dob is not entered, it will just be null
            dob = dob if dob else None
            new_user = Users(email=email, first_name=first_name, last_name=last_name, password=password1, dob=dob)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')

            create_collection(new_user.user_id)

            return redirect(url_for('views.login'))

    return render_template('sign_up.html')


# for now to make sure POST is working in the login page
@views.route('/profile/', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('password1')
        dob = request.form.get('dob')

        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')

        update_allowed = True  # Flag to check that all changes can be made.
        # check if email is being changed and if new email already exists.
        if email != current_user.email:
            user = Users.query.filter_by(email=email).first()
            if user:
                flash('This Email already exists.', category='error')
                update_allowed = False
            elif len(email) > 40:
                flash('Email must be at most 40 characters', category='error')
                update_allowed = False
            else:
                current_user.email = email

        # validate that a new password was provided.
        if new_password:
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            if not (3 <= len(new_password) <= 50):
                flash('New password must be between 3 and 50 characters')
                update_allowed = False
            elif password1 != password2:
                flash('Passwords do not match', category='error')
                update_allowed = False
            else:
                current_user.password = new_password

        # update is only made to the database when it passed all the if statements.
        if update_allowed:
            current_user.dob = dob if dob else None
            db.session.commit()
            flash('Profile updated successfully.', category='success')

    return render_template('profile.html', user=current_user.first_name)


def create_collection(user_id):
    query = text("""
        INSERT INTO gamecollection (user_id)
        VALUES (:user_id)
    """)

    try:
        db.session.execute(query, {'user_id': user_id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('collection added')


@views.route('/games/', methods=['POST', 'GET'])
def games():
    user_id = current_user.user_id if current_user.is_authenticated else None
    game = db.session.execute(text("SELECT * FROM games ORDER BY title")).fetchall()

    if request.method == 'POST' and current_user.is_authenticated:
        game_id = int(request.form.get('add') or request.form.get('remove'))

        collection_id = get_collection_id(user_id)

        if request.form.get('add'):
            add_game_to_collection(game_id, collection_id)
        elif request.form.get('remove'):
            remove_game_from_collection(game_id, collection_id)

        # should get the changes of the database after adding/remove was made

        query = text("""
            SELECT * FROM games ORDER BY title
        """)
        game = db.session.execute(query).fetchall()

    # game_in_collection is passed by in html to display - and + and also determine if the action is add or remove
    return render_template('games.html', games=game, game_in_collection=game_in_collection)


# to get the user's collection id
# this is used to pass it to add_game_to_collection and remove_game_from_collection
def get_collection_id(user_id):
    query = text("""
        SELECT collection_id
        FROM gamecollection
        WHERE user_id = :user_id
    """)

    collection_id = db.session.execute(query, {'user_id': user_id}).scalar()

    return collection_id


# to check if game is in collection, if an id is returned it's true
# this is done by the if statement in both games.html and collection.html
# { % if game_in_collection(collections.game_id, current_user.user_id) %}
def game_in_collection(game_id, user_id):
    query = text("""
        SELECT collection_id FROM gamecollectionitems
        WHERE game_id = :game_id AND collection_id IN (
            SELECT collection_id FROM gamecollection WHERE user_id = :user_id)
    """)

    collection_id = db.session.execute(query, {'game_id': game_id, 'user_id': user_id}).fetchall()

    return collection_id


# function for button to add game from collection
def add_game_to_collection(game_id, collection_id):
    query = text("""
        INSERT INTO gamecollectionitems (game_id, collection_id)
        VALUES (:game_id, :collection_id)
    """)

    db.session.execute(query, {'game_id': game_id, 'collection_id': collection_id})
    db.session.commit()


# function for the button to remove games from collection
def remove_game_from_collection(game_id, collection_id):
    query = text("""
        DELETE FROM gamecollectionitems
        WHERE game_id = :game_id AND collection_id = :collection_id
    """)

    db.session.execute(query, {'game_id': game_id, 'collection_id': collection_id})
    db.session.commit()


@views.route('/collection/', methods=['POST', 'GET'])
@login_required
def collection():
    query = text("""
         SELECT gci.*, g.* 
         FROM gamecollectionitems gci
         JOIN games g ON gci.game_id = g.game_id
         WHERE gci.collection_id IN (
             SELECT gc.collection_id
             FROM gamecollection gc
             WHERE gc.user_id = :user_id)
         ORDER BY g.title
     """)

    user_id = current_user.id

    # same logic as /games/ endpoint, but only remove is used here.
    if request.method == 'POST':
        user_id = current_user.id
        game_id = int(request.form.get('remove'))

        collection_id = get_collection_id(user_id)

    if request.form.get('remove'):
        remove_game_from_collection(game_id, collection_id)

    collections = db.session.execute(query, {'user_id': user_id}).fetchall()

    return render_template('collection.html', collections=collections, game_in_collection=game_in_collection)

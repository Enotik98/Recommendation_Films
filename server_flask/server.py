from flask import Flask, jsonify, request, g
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import movie_recommender
import numpy as np
import database
import hashlib
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app)

def generate_token(user_id, expiration):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps({'user_id': user_id}, salt='token-salt')
    return token

def verify_token(token):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='token-salt')
        return data['user_id']
    except SignatureExpired:
        return None
    except BadSignature:
        # Недійсний токен
        return None


@app.before_request
def check_token():
    token = request.headers.get('Authorization')
    if token:
        token = token.split(' ')[1]
        user_id = verify_token(token)
        if user_id:
            g.user_id = user_id
            return
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    return

@app.route('/registration', methods=['POST'])
def registration_user():
    data = request.json
    usrname = data['username']
    password = data['password']
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    conn = database.connect_to_database()
    cursor = conn.cursor()
    query = "INSERT INTO users(username, password) VALUES (%s, %s);"
    cursor.execute(query, (usrname, hash_password))
    conn.commit()
    cursor.close()
    conn.close()
    response = {'message': 'add user successfully'}
    return jsonify(response)

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    usrname = data['username']
    password = data['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = database.connect_to_database()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = %s AND password = %s;"
    cursor.execute(query, (usrname, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        access = generate_token(user[0], expiration=60)
        refresh = generate_token(user[0], expiration=86400)
        response = {'accessToken': access, 'refreshToken': refresh}
    else:
        response = {'message': 'Invalid username or password'}
    return jsonify(response)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    user_id = getattr(g, 'user_id', None)
    if user_id != None:
        data = request.json
        conn = database.connect_to_database()
        cursor = conn.cursor()
        query = "INSERT INTO movies(user_id, movie) VALUES (%s, %s);"
        cursor.execute(query, (user_id, data['movie']))
        conn.commit()
        cursor.close()
        conn.close()
        response = {'message': 'add movie successfully'}
    else:
        response = {'message': 'Unauthorized'}
    return jsonify(response)


@app.route('/movie', methods=['GET'])
def get_user_movies():
    user_id = getattr(g, 'user_id', None)
    print(user_id)
    if user_id != None:
        conn = database.connect_to_database()
        cursor = conn.cursor()
        query = "SELECT movie FROM movies WHERE user_id = %s;"
        cursor.execute(query, (user_id, ))

        movies = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        response = {'movies': movies}
    else:
        response = {'message': 'not foud id'}, 403
    return jsonify(response)
    
@app.route('/recommendations', methods=['POST'])
def recommend_movies():
    data = request.json
    if data['user_movie']:
        user_movie = data['user_movie']
    else:
        user_movie = []
    print(user_movie)
    if data['genre']:
        print('not empty')
    else:
        print('empty')
    genre = data['genre']
    print(genre)
    rating = data['rating']
    print(rating)
    recommendations, scores = movie_recommender.model.get_recommendations(user_movie, genre, rating)
    print(recommendations)
    response = {'recommendations': np.array(recommendations).tolist(), 'score': np.array(scores).tolist()}
    return jsonify(response)

if __name__ == '__main__':
    app.run()
from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from bson import json_util
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['MONGO_URI']='mongodb+srv://admin:admin@cluster0.wepwf.mongodb.net/prueba?retryWrites=true&w=majority'
mongo = PyMongo(app)

@app.route('/users', methods=['POST'])
def create_user():
    print(request.json)
    username = request.json['username']
    mongo.db.users.insert_one(
        {'username':username}
    )
    return {'message':'received'}

@app.route('/songs', methods=['GET'])
def see_songs():
    songs = mongo.db.songs.find()
    response = json_util.dumps(songs)
    return Response(response, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True)

import sys
import os
import pymongo
import flickrapi

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from werkzeug.utils import secure_filename 


api_key = u'19842a35780dcd90c170d75f5d5b168c'
api_secret = u'bf1442c3ef944853'

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='read')
photos = flickr.photos.search(user_id='73509078@N00', per_page='10')
sets = flickr.photosets.getList(user_id='73509078@N00') 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './fotos'

uri = 'mongodb+srv://ruben:ingweb21@clusterruben.83p20.mongodb.net/ingweb?retryWrites=true&w=majority'

client = pymongo.MongoClient(uri)

db = client.get_default_database() 

global idtoken
global correo

@app.route('/', methods=['GET'])
def default():
    return render_template('loginOauth.html')


@app.route('/login', methods=['POST'])
def login_oauth():
    global correo
    global idtoken
    imagenes = db['imagenes']
    correo = request.form['correo']
    idtoken = request.form['idtoken']

    try:
        CLIENT_ID = '195742355808-v7fljt7gjvb2q5jn6hrmkpkbqtsh3ie0.apps.googleusercontent.com'
        id_token.verify_oauth2_token(idtoken, requests.Request(), CLIENT_ID)

    except ValueError:
        return render_template('loginOauth.html', error="Error de verificación")

    return render_template('images.html',imagenes = list(imagenes.find().sort('likes',pymongo.DESCENDING)), correo = correo)

@app.route('/fotos/<nombre>', methods = ['GET', 'POST'])
def foto(nombre):

    if(comprobarToken()==0):
        return render_template('loginOauth.html', error="Error de verificación")

    return send_from_directory(app.config['UPLOAD_FOLDER'], nombre)

@app.route('/imagenes', methods = ['GET'])
def imagenes():
    imagenes = db['imagenes']

    if(comprobarToken()==0):
        return render_template('loginOauth.html', error="Error de verificación")

    return render_template('images.html', imagenes = list(imagenes.find().sort('likes',pymongo.DESCENDING)), correo = correo)


@app.route('/like/<_id>/<num>', methods = ['GET', 'POST'])
def like(_id, num):
    imagenes = db['imagenes']

    numlike = int(num)
    
    img = { 'likes': str(numlike+1) }
    imagenes.update_one({'_id': ObjectId(_id) }, { '$set': img })   

    #return render_template('images.html', imagenes = list(imagenes.find().sort('likes',pymongo.DESCENDING)), correo = correo)
    return redirect(url_for('imagenes'))

@app.route('/editar/<_id>/<desc>', methods = ['GET', 'POST'])
def editar(_id, desc):
    imagenes = db['imagenes']
    
    if request.method == 'GET' :
        return render_template('editar.html', desc = desc, _id = _id)

    else:
        i = { 'descripcion': request.form['descripcion'] }
        imagenes.update_one({'_id': ObjectId(_id) }, { '$set': i })   

    return redirect(url_for('imagenes'))

@app.route('/eliminar/<_id>', methods = ['GET', 'POST'])
def eliminar(_id):
    imagenes = db['imagenes']
    
    imagenes.delete_one({'_id': ObjectId(_id) })   

    return redirect(url_for('imagenes'))
        

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    imagenes = db['imagenes']

    if(comprobarToken()==0):
        return render_template('loginOauth.html', error="Error de verificación")

    if request.method == 'GET' :
        return render_template('nuevo.html')

    else:
        f = request.files['archivo']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        nueva_img = {'usuario': correo,
              'nombre': filename, 
              'descripcion': request.form['descripcion'],
              'likes': 0
             }
        imagenes.insert_one(nueva_img)
        return render_template('images.html', imagenes = list(imagenes.find().sort('likes',pymongo.DESCENDING)), correo = correo)


def comprobarToken():
    try:
        CLIENT_ID = '195742355808-v7fljt7gjvb2q5jn6hrmkpkbqtsh3ie0.apps.googleusercontent.com'
        id_token.verify_oauth2_token(idtoken, requests.Request(), CLIENT_ID)

    except ValueError:
        return 0

    return 1   

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App Engine
    # or Heroku, a webserver process such as Gunicorn will serve the app. In App
    # Engine, this can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True) 
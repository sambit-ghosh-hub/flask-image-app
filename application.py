import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import random

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import boto3
import os

from dotenv import load_dotenv
load_dotenv()

ACCESS_KEY=os.environ['IMAGEUSER_AK']
ACCESS_SECRET=os.environ['IMAGEUSER_AS']
DATABASE_PASS=os.environ['DATABASE_PASS']

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
#hvpass2023
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{DATABASE_PASS}@devopsflask.c312bt5ys4k2.us-east-1.rds.amazonaws.com:5432/devopsflask"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()

class UserModel(db.Model):
    __tablename__ = 'filedata'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    filename = db.Column(db.String())


    def __init__(self, id,name, filename):
        self.id = id
        self.name = name
        self.filename = filename

db.create_all()
@app.route('/')
def index():
    return jsonify({'hello': 'world'})

@app.route('/userDetails')
def userDetails():
    return "WIP"

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/fileupload', methods=['POST'])
def uploadUserData():
	# check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name = request.form.get('name')
        id = request.form.get('id')
        print(id,name)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filename = str(random.randint(1,1000))+filename
        entry = UserModel(id=id,name=name,filename=filename)
        db.session.add(entry)
        db.session.commit()
        session = boto3.Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=ACCESS_SECRET)
        s3 = session.resource('s3')
        
        # file.save(os.path.join('UPLOAD_FOLDER', filename))
        # data = open('test.jpg', 'rb')
        s3.Bucket('devbucket-sam').put_object(Key=filename, Body=file)

        resp = jsonify({'message' : 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp

if __name__=="__main__":
    app.run(debug=True)
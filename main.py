# FileUpload.py
import zipfile

from flask import Flask, json, request, jsonify
import os
import shutil
import random

from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from train import startTraining

app = Flask(__name__)

UPLOAD_FOLDER = 'static/UPLOADS'  # relative path to the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for the file uploads to prevent memory issues

ALLOWED_EXTENSIONS = set(['zip', 'jpg', 'jpeg', 'png'])  # set of allowed file extensions

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})  # allow all origins for now

HOMEPAGE_HTML = '''<html>
                <head>
                    <title>DATASET UPLOAD</title> 
                    <style>
                        .alert {
                          padding: 20px;
                          background-color: #f44336;
                          color: white;
                          opacity: 1;
                          transition: opacity 0.6s;
                          margin-bottom: 15px;
                        }
                        
                        .alert.success {background-color: #04AA6D;}
                        .alert.info {background-color: #2196F3;}
                        .alert.warning {background-color: #ff9800;}
                        
                        .closebtn {
                          margin-left: 15px;
                          color: white;
                          font-weight: bold;
                          float: right;
                          font-size: 22px;
                          line-height: 20px;
                          cursor: pointer;
                          transition: 0.3s;
                        }
                        
                        .closebtn:hover {
                          color: black;
                        }
                    </style>
                </head>
                <body>
                    <form action="http://127.0.0.1:5000/upload" method="POST" enctype="multipart/form-data">\
                    
                     </br> 
                      <label for="files">Select files:</label>
                      <input type="file" id="files" name="files" multiple><br><br>
                      <input type="submit">
                      </br>
                      </br> 
                      <div></div>
                    </form>
                </body>
            </html>'''

ERROR_MSG = '''<div class="alert">
                            <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                            <strong>Danger!</strong>  </br> </br> ###
              </div>'''

SUCCESS_MSG = '''<div class="alert success">
                            <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                            <strong>SUCCESS!</strong> </br> </br> ###
              </div>'''

INFO_MSG = '''<div class="alert info">
                            <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                            <strong>RESULT:</strong> </br> </br> ###
              </div>'''



def allowed_file(filename):  # check if the file is allowed to be uploaded
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return HOMEPAGE_HTML


@app.route('/upload', methods=['POST'])
@cross_origin(origin='*')
def upload_file():
    # check if the post request has the file part
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    print(request.files)
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files')
    print('=================================================')
    print(len(files))
    print('=================================================')
    errors = {}
    success = False

    print("creating folders")
    os.makedirs('./static/UPLOADS/', exist_ok=True)
    os.makedirs('./static/TRAIN/dogs/', exist_ok=True)
    os.makedirs('./static/TRAIN/cats/', exist_ok=True)
    os.makedirs('./static/TEST/', exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print(format(filename))
            print(filename.rsplit('.', 1)[1].lower())
            if filename.rsplit('.', 1)[1].lower() == 'zip':
                print("zip file found")
                with zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as zip_ref:
                    zip_ref.extractall('./static/UPLOADS/')
                print("zip file extracted")
            success = True
        else:
            errors['Message'] = file.filename + ' File type is not allowed'
            success = False

    if success and errors:  # if there are errors, return them
        resp = jsonify({'Message': 'File(s) successfully uploaded', 'success': success, 'errors': errors})
        resp.status_code = 500
        return resp
    if success:
        distribute_train_validation_split(0.25)
        result = startTraining()  # start training
        # resp = jsonify({'Message': 'Files successfully uploaded and training also done',
        #                 'Loss': result.history['loss'],
        #                 'Accuracy': result.history['accuracy'],
        #                 'Epochs': result.params['epochs'],
        #                 'Steps': result.params['steps']})

        # resp.status_code = 201
        # return resp

        msg1 = 'Files successfully uploaded and training also done!!'
        msg2 = '''Epochs: {} <br>
                    Steps: {} <br> 
                    Loss: {} <br>
                    Accuracy: {}  
                    '''.format(result.params['epochs'],
                               result.params['steps'],
                               result.history['loss'],
                               result.history['accuracy']
                               )
        return HOMEPAGE_HTML.replace("<div></div>", SUCCESS_MSG.replace("###", msg1) + INFO_MSG.replace("###", msg2) )

    else:
        return HOMEPAGE_HTML.replace("<div></div>", ERROR_MSG.replace("###", errors['Message']))


def distribute_train_validation_split(validation_size=0.2):
    all_images = os.listdir('./static/uploads')
    # random.shuffle(all_images)
    # print("randoom shuffle done")
    all_dogs = list(filter(lambda image: 'dog' in image, all_images))
    all_cats = list(filter(lambda image: 'cat' in image, all_images))

    print("cats dogs seperated")

    index_to_split_cat = int(len(all_cats) * validation_size)
    index_to_split_dog = int(len(all_dogs) * validation_size)

    print(index_to_split_cat)
    print(index_to_split_dog)

    training_dogs = all_dogs[index_to_split_dog:]
    validation_dogs = all_dogs[:index_to_split_dog]
    training_cats = all_cats[index_to_split_cat:]
    validation_cats = all_cats[:index_to_split_cat]

    print("coping files....................................")
    copy_images_to_dir(training_dogs, './static/TRAIN/dogs')
    copy_images_to_dir(training_cats, './static/TRAIN/cats')

    copy_images_to_dir(validation_cats, './static/TEST')
    copy_images_to_dir(validation_dogs, './static/TEST')


def copy_images_to_dir(images_to_copy, destination):
    for image in images_to_copy:
        shutil.move(f'./static/UPLOADS/{image}', f'{destination}/{image}')


if __name__ == '__main__':
    app.run(debug=True)

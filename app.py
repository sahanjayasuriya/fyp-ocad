from os import path, getcwd

from flask import Flask, Response, json, request
from werkzeug.utils import secure_filename

from db import Database
from face_recognizer import FaceRecognizer
from facebook_scraper import FacebookScraper
from image_classifier import ImageClassifier

app = Flask(__name__)
from test import *

app.config['file_allowed'] = ['image/png', 'image/jpg', 'image/jpeg']
app.config['storage'] = path.join(getcwd(), 'storage')
app.db = Database()
app.face_recognizer = FaceRecognizer(app)
app.image_classifier = ImageClassifier(app)
app.facebook_scraper = FacebookScraper(app)


def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)


def error_handle(error_message, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": {"message": error_message}}), status=status, mimetype=mimetype)


@app.route('/', methods=['GET'])
def home():
    output = json.dumps({"api": "1.0"})
    return success_handle(output)


@app.route('/api/v1/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return error_handle("Face image is required")
    else:
        file = request.files['file']
        if file.mimetype not in app.config['file_allowed']:
            error_handle("Only png, jpg and jpeg are allowed")
        else:
            name = request.form['name']
            if 'name' not in request.form:
                return error_handle("Name is required")
            else:
                filename = secure_filename(file.filename)
                user_image_path = path.join(app.config['storage'], 'users')
                file.save(path.join(user_image_path, filename))

                face_result = app.face_recognizer.recognize(filename)

                success_results = []
                error_results = []
                if face_result:
                    for face_image in face_result:
                        predict_result = app.image_classifier.predict(face_image['filename'])
                        if predict_result:
                            success_results.append(predict_result)
                        else:
                            error_results.append(predict_result)
                    print(success_results)
                    print(error_results)
                    return success_handle(str(success_results) + " " + str(error_results))
                else:
                    return error_handle(
                        "Face not found in library")


@app.route('/api/v1/train', methods=['GET'])
def train_model():
    return success_handle(app.image_classifier.train())


@app.route('/api/v1/crawl/facebook', methods=['POST'])
def crawl_facebook():
    link = request.form['link']
    if 'link' not in request.form:
        return error_handle("Facebook page link is required")
    else:
        count = app.facebook_scraper.crawl(link)
        return success_handle("Crawling finished. " + str(count) + ' new photos added to the library.')


if __name__ == "__main__":
    app.run()

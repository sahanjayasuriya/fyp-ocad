from app import app
from os import path
from flask import Flask, Response, request, json
from werkzeug.utils import secure_filename


def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)


def error_handle(error_message, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": {"message": error_message}}), status=status, mimetype=mimetype)


@app.route('/api/v1/recognize', methods=['POST'])
def recognize():
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

                result = app.face_recognizer.recognize(filename)
                if result:
                    message = {"message": result}
                    return success_handle(json.dumps(message))
                else:
                    return error_handle(
                        "Face not found in library")


@app.route('/api/v1/predict', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return error_handle("Image is required")
    else:
        file = request.files['file']
        if file.mimetype not in app.config['file_allowed']:
            error_handle("Only png, jpg and jpeg are allowed")
        else:
            filename = secure_filename(file.filename)
            user_image_path = path.join(app.config['storage'], 'predict')
            file.save(path.join(user_image_path, filename))

            result = app.image_classifier.predict(filename)
            if result:
                return success_handle(result)
            else:
                return error_handle(
                    "Error")


@app.route('/api/v1/test', methods=['GET'])
def test():
    app.face_recognizer.save_face_encodings()
    return success_handle("Test")

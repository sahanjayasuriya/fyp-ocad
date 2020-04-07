import pickle
from os import path

import face_recognition


class FaceRecognizer:
    def __init__(self, app):
        self.storage = app.config["storage"]
        self.db = app.db
        self.library = []
        self.face_encodings = {}
        self.library_faces_encoded = []
        self.load_face_encodings()
        self.load_faces()

    def load_library_image_by_key(self, name):
        library_storage = path.join(self.storage, 'library')
        return path.join(library_storage, name)

    def load_library_image_by_name(self, name):
        user_storage = path.join(self.storage, 'library')
        return path.join(user_storage, name)

    def load_user_image_by_name(self, name):
        user_storage = path.join(self.storage, 'users')
        return path.join(user_storage, name)

    def load_face_encodings(self):
        with open('dataset_faces.dat', 'rb') as f:
            self.face_encodings = pickle.load(f)

    def load_faces(self):
        print("Face data loading started")
        results = self.db.select(
            'SELECT lib.id, lib.filename, lib.face_encoding FROM image_library lib WHERE lib.face_encoding = 1')

        for row in results:
            image_id = row[0]
            filename = row[1]

            image = {
                "id": image_id,
                "filename": filename
            }

            self.library.append(image)
            self.library_faces_encoded.append(self.face_encodings[image_id])
        print("Face data loading complete")

    def recognize(self, user_filename):
        user_image = face_recognition.load_image_file(self.load_user_image_by_name(user_filename))
        user_encoding_image = face_recognition.face_encodings(user_image)[0]

        results = face_recognition.compare_faces(self.library_faces_encoded, user_encoding_image)

        print("results", results)

        index_key = 0
        result_images = []
        for matched in results:

            if matched:
                result_images.append(self.library[index_key])

            index_key = index_key + 1

        return result_images

    def save_face_encodings(self):
        results = self.db.select('SELECT lib.id, lib.filename FROM image_library lib')
        photo_count = 0
        save_count = 0
        all_face_encodings = {}
        for row in results:
            image_id = row[0]
            filename = row[1]

            face_image = face_recognition.load_image_file(self.load_library_image_by_name(filename))
            face_encodings = face_recognition.face_encodings(face_image)
            photo_count += 1
            if len(face_encodings) != 0:
                all_face_encodings[image_id] = face_encodings[0]
                self.db.update('UPDATE image_library SET face_encoding = 1 WHERE id = ?',
                               [image_id])
                save_count += 1

            print(str(photo_count) + " photos processed. " + str(save_count) + " face data saved")
        with open('dataset_faces.dat', 'wb') as f:
            pickle.dump(all_face_encodings, f)

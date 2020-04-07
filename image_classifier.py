import datetime
import os
from os import path

import tensorflow as tf
import matplotlib.image as mpimg
from skimage.transform import resize

basedir = "storage/image_classification"
train_dir = os.path.join(basedir, "train/")
test_dir = os.path.join(basedir, "test/")
val_dir = os.path.join(basedir, "validation/")


class ImageClassifier:

    def __init__(self, app):
        print('Image classifier initialized')
        self.storage = app.config["storage"]

    def train(self):
        print('Train model')

        train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
        test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
        val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(150, 150),
            batch_size=50,
            class_mode='binary'
        )

        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(150, 150),
            batch_size=50,
            class_mode='binary'
        )

        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=(150, 150),
            batch_size=50,
            class_mode='binary'
        )

        epochs = 1

        model = self.create_model()

        model.summary()

        model.compile(loss="binary_crossentropy", optimizer=tf.keras.optimizers.Adam(lr=0.003), metrics=['acc'])

        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3),
            tf.keras.callbacks.ModelCheckpoint('./' + str(datetime.datetime.now()), monitor='val_acc'),
            tf.keras.callbacks.TensorBoard(histogram_freq=0)
        ]

        model.fit_generator(
            train_generator,
            steps_per_epoch=100,
            epochs=epochs,
            validation_data=val_generator,
            validation_steps=50,
            callbacks=callbacks)

        model.save_weights('storage/models/ocad-model.h5')

        return "Training complete"

    def predict(self, image_to_predict):
        model = self.create_model()
        model.load_weights('storage/models/ocad-model.h5')
        img_path = self.load_predict_image_by_name(image_to_predict)
        img = mpimg.imread(img_path)
        resized = resize(img, (150, 150), anti_aliasing=True)
        pred = model.predict(resized.reshape((1, 150, 150, 3)))[0]

        return ('MEME' if pred >= 0.5 else 'LAME PIC') + " " + str(pred[0])

    def load_predict_image_by_name(self, name):
        user_storage = path.join(self.storage, 'library')
        return path.join(user_storage, name)

    def create_model(self):
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Conv2D(32, (5, 5), activation='relu', input_shape=(150, 150, 3)))
        model.add(tf.keras.layers.MaxPooling2D((2, 2)))
        model.add(tf.keras.layers.Conv2D(64, (5, 5), activation='relu'))
        model.add(tf.keras.layers.MaxPooling2D((2, 2)))
        model.add(tf.keras.layers.Conv2D(128, (3, 3), activation='relu'))
        model.add(tf.keras.layers.MaxPooling2D((2, 2)))
        model.add(tf.keras.layers.Conv2D(128, (3, 3), activation='relu'))
        model.add(tf.keras.layers.MaxPooling2D((2, 2)))
        model.add(tf.keras.layers.Flatten())
        model.add(tf.keras.layers.Dense(512, activation='relu'))
        model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
        return model

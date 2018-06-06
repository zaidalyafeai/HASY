#!/usr/bin/env python

"""
Trains a simple convnet on the HASY dataset.

Gets to 77.77% test accuracy after 1 epoch.
790 seconds per epoch on a GeForce 940MX GPU.
"""

from __future__ import print_function
import numpy as np
np.random.seed(0)  # make sure results are reproducible

import tensorflow as tf
tf.set_random_seed(0)  # make sure results are reproducible
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers.advanced_activations import PReLU
from keras.optimizers import Adam
from keras import backend as K

import hasy_tools as ht

batch_size = 128
nb_epoch = 1

# input image dimensions
img_rows, img_cols = ht.img_rows, ht.img_cols

# Load data
fold = 1
hasy_data = ht.load_data(mode='fold-{}'.format(fold), image_dim_ordering='tf')

x_train = hasy_data['x_train']
y_train = hasy_data['y_train']
x_test = hasy_data['x_test']
y_test = hasy_data['y_test']

# One-Hot encoding
y_train = np.eye(ht.n_classes)[y_train.squeeze()]
y_test = np.eye(ht.n_classes)[y_test.squeeze()]

# Preprocessing
x_train = ht.preprocess(x_train)
x_test = ht.preprocess(x_test)

# Define model
model = Sequential()
model.add(Convolution2D(32, (3, 3),
                        padding='same',
                        input_shape=x_train.shape[1:], activation='relu'))
model.add(Convolution2D(64, (3, 3), padding='same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(1024, activation='tanh'))
model.add(Dropout(0.5))
model.add(Dense(ht.n_classes, activation='softmax'))

# Train model
adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
model.compile(loss='categorical_crossentropy',
              optimizer=adam,
              metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=batch_size, epochs=nb_epoch,
          verbose=1, validation_data=(x_test, y_test))

# Serialize model
model.save('keras.h5')

# Evaluate model
score = model.evaluate(x_test, y_test, verbose=0)
print('Test accuarcy: {:0.2f}%'.format(score[1] * 100))

prediction = model.predict(x_test[0].reshape(-1, img_rows, img_cols), 1)
# only show first 3 probabilities
print("Prediction: {}".format(str(prediction[0][:3])))

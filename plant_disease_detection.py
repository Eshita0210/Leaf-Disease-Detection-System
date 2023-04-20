# -*- coding: utf-8 -*-
"""Plant_Disease_Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fKYU-6KemXLt9jBjURWsZZTd1VOvSQfD
"""

#install kaggle
!pip install -q kaggle

from google.colab import files
files.upload()

#create a kaggle folder
!mkdir ~/.kaggle

#copy the kaggle.json to folder created
!cp kaggle.json ~/.kaggle/

#Permission for the json to act
!chmod 600 ~/.kaggle/kaggle.json

#to list all datasets in kaggle
!kaggle datasets list

!kaggle datasets download -d vipoooool/new-plant-diseases-dataset

!unzip new-plant-diseases-dataset.zip

#importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

import keras
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import load_img
from tensorflow.keras.utils import img_to_array
from keras.applications.vgg19 import VGG19, preprocess_input,decode_predictions

#EDA
len(os.listdir("/content/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)/train"))

train_datagen = ImageDataGenerator(zoom_range=0.5, shear_range=0.3, horizontal_flip=True,preprocessing_function=preprocess_input)
val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

#preprocessing of data using builtin function (preprocessing_input)
train = train_datagen.flow_from_directory(directory= "/content/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)/train", 
                                          target_size=(256,256), 
                                          batch_size=32)
val = val_datagen.flow_from_directory(directory= "/content/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)/valid", 
                                          target_size=(256,256), 
                                          batch_size=32)

t_img, label=train.next()

t_img.shape

def plotImage(img_arr,label):
  for im, l in zip(img_arr,label):
    plt.figure(figsize=(5,5))
    plt.imshow(im)
    plt.show()

#visualising our data
plotImage(t_img[:3],label[:3])

"""# Building The Model"""

from keras.layers import Dense, Flatten
from keras.models import Model
from keras.applications.vgg19 import VGG19
import keras

base_model = VGG19(input_shape=(256,256,3), include_top=False)

for layer in base_model.layers:
  layer.trainable = False

base_model.summary()

X = Flatten()(base_model.output)
X = Dense(units = 38,activation = 'softmax')(X)

#Creating the model
model = Model(base_model.input, X)

model.summary()

model.compile(optimizer='adam', 
              loss=keras.losses.categorical_crossentropy,
              metrics=['accuracy'])

"""# Early Stopping and Model Check point"""

from keras.callbacks import ModelCheckpoint, EarlyStopping

#early stopping
es = EarlyStopping(monitor='val_accuracy',
                   min_delta = 0.01, 
                   patience = 3, 
                   verbose=1)

#model check point 
mc = ModelCheckpoint(filepath='best_model.h5',
                     monitor='val_accuracy',
                     min_delta = 0.01, 
                     patience = 3, 
                     verbose=1)

cb = [es,mc]

his = model.fit_generator(train,
                          steps_per_epoch=16,
                          epochs=50,
                          verbose=1,
                          callbacks=cb,
                          validation_data=val,
                          validation_steps=16)

#plotting the model
h=his.history
h.keys()

plt.plot(h['accuracy'])
plt.plot(h['val_accuracy'],c="red")
plt.title("acc vs v-acc")
plt.show()

plt.plot(h['loss'])
plt.plot(h['val_loss'],c="red")
plt.title("loss vs v-loss")
plt.show()

#load best model
from keras.models import load_model
model = load_model("/content/best_model.h5")

#evaluation of our model
acc = model.evaluate_generator(val)[1]
print(f"The accuracy of your model is= {acc*100}%")

ref = dict(zip(list(train.class_indices.values()) , list(train.class_indices.keys())))
ref

def prediction(path):
  img = load_img(path,target_size = (256,256))
  i = img_to_array(img)
  im = preprocess_input(i)
  img = np.expand_dims (im,axis=0)
  pred = np.argmax(model.predict(img))
  print(f"The image belongs to: {ref[pred]}")

path = "/content/test/test/AppleCedarRust4.JPG"
prediction(path)
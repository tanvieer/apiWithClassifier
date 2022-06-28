import keras
from keras_preprocessing.image import ImageDataGenerator



def startTraining():

    train_imagedatagenerator = ImageDataGenerator(rescale=1/255.0)
    validation_imagedatagenerator = ImageDataGenerator(rescale=1/255.0)

    train_iterator = train_imagedatagenerator.flow_from_directory(
        './static/TRAIN',
        target_size=(150, 150),
        batch_size=8,
        class_mode='binary')

    validation_iterator = validation_imagedatagenerator.flow_from_directory(
        './static/TEST',
        target_size=(150, 150),
        batch_size=8,
        class_mode='binary')


    model = keras.Sequential([
        keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=(150, 150, 3)),
        keras.layers.MaxPool2D((2, 2)),
        keras.layers.Conv2D(32, (3, 3), activation='relu'),
        keras.layers.MaxPool2D((2, 2)),
        keras.layers.Conv2D(64, (3, 3), activation='relu'),
        keras.layers.MaxPool2D((2, 2)),
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    #model.compile(optimizer='adam', loss='binary_cross_entropy', metrics=['accuracy'])
    model.compile(optimizer='adam', loss=keras.losses.binary_crossentropy, metrics=['accuracy'])
    #model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    model.summary()
    model.save_weights("./static/model_weights.h5")
    model.save("./static/model.h5")


    history = model.fit(train_iterator,
                        validation_data=validation_iterator,
                        steps_per_epoch=20,
                        epochs=5,
                        validation_steps=20)

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    print('Loss = ')
    print(history.history['loss'])

    print('Accuracy = ')
    print(history.history['accuracy'])

    print('Epochs = ')
    print(history.params['epochs'])

    print('Steps = ')
    print(history.params['steps'])

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    model.save("./static/model.h5")


    return history



#=======================================================
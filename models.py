import tensorflow as tf 
from tensorflow.keras import models
from tensorflow.keras import layers


class MobileNetV3():
    def __init__(self, image_shape, lables_num):
        self.base_model = tf.keras.applications.MobileNetV3Small(input_shape=(*image_shape, 3), alpha=1.0, minimalistic=False, include_top=False,
            weights='imagenet', input_tensor=None, pooling='avg')
        self.labels_num = lables_num
        self.model = None
        self.image_shape = image_shape

    def model_summary(self, detailed = False):
        if detailed :
            self.base_model.summary()
        self.model.summary()
    
    def build_mobileNetV3_1a(self,dropout_rate = 0.2):
        """
        Build model for task 1a - tunning only classificator
        """

        for layer in self.base_model.layers:
            layer.trainable = False
        
        base_output_shape = self.base_model.get_layer('avg_pool').output_shape[1]

        self.model = models.Sequential()
        self.model.add(self.base_model)
        self.model.add(layers.Reshape((1,1,base_output_shape)))
        if dropout_rate > 0:
            self.model.add(layers.Dropout(dropout_rate))
        self.model.add(layers.Conv2D(self.labels_num, kernel_size=1, padding='same'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Activation('softmax'))

        self.model.summary()

    def build_mobileNetV3_2a(self, dropout_rate=0.2):
        """
        Build model for task 2a - tunning last convolutional layer and classificator
        """

        for layer in self.base_model.layers:
            layer.trainable = False
        
        self.base_model.get_layer('Conv_2').trainable = True
        base_output_shape = self.base_model.get_layer('avg_pool').output_shape[1]

        self.model = models.Sequential()
        self.model.add(self.base_model)
        self.model.add(layers.Reshape((1,1,base_output_shape)))
        if dropout_rate > 0:
            self.model.add(layers.Dropout(dropout_rate))
        self.model.add(layers.Conv2D(self.labels_num, kernel_size=1, padding='same'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Activation('softmax'))

        self.model.summary()

    
    def build_mobileNetV3_2b(self, dropout_rate=0.2):
        """
        Build model for task 2b - tunning two last convolutional layer and classificator
        """

        for layer in self.base_model.layers:
            layer.trainable = False
        
        self.base_model.get_layer('Conv_2').trainable = True
        self.base_model.get_layer('Conv_1').trainable = True
        self.base_model.get_layer('Conv_1/BatchNorm').trainable = True
        base_output_shape = self.base_model.get_layer('avg_pool').output_shape[1]

        self.model = models.Sequential()
        self.model.add(self.base_model)
        self.model.add(layers.Reshape((1,1,base_output_shape)))
        if dropout_rate > 0:
            self.model.add(layers.Dropout(dropout_rate))
        self.model.add(layers.Conv2D(self.labels_num, kernel_size=1, padding='same'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Activation('softmax'))

        self.model.summary()


    def build_mobileNetV3_2c(self, dropout_rate=0.2, weights = False):
        """
        Build model for task 2c - train all layers

        Args:
            weights - if True - imagenet weight loaded, else random initializer
        """
        if weights :
            base_model = self.base_model
        else:
            base_model =  tf.keras.applications.MobileNetV3Small(input_shape=(*self.image_shape, 3), alpha=1.0, minimalistic=False, include_top=False,
                weights=None, input_tensor=None, pooling='avg')

        for layer in base_model.layers:
            layer.trainable = True

        base_output_shape = base_model.get_layer('avg_pool').output_shape[1]

        self.model = models.Sequential()
        self.model.add(base_model)
        self.model.add(layers.Reshape((1,1,base_output_shape)))
        if dropout_rate > 0:
            self.model.add(layers.Dropout(dropout_rate))
        self.model.add(layers.Conv2D(self.labels_num, kernel_size=1, padding='same'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Activation('softmax'))

        self.model.summary()

    def train_with_generator(self, image_generator, epochs, optimizer = 'Adam', loss ='categorical_crossentropy', 
                                metrics =['accuracy'], callbacks = None):

        if self.model is None:
            raise TypeError('Model is NoneType object - not build')

        self.model.compile(optimizer = optimizer, 
                        loss=loss,
                        metrics = metrics)

        history = self.model.fit(        
            image_generator.train_generator(),        
            epochs = epochs,
            callbacks = callbacks,
            validation_data = image_generator.validation_generator())

        return history

  
    def train_with_arrays(self, image_generator, epochs, optimizer = 'Adam', loss ='categorical_crossentropy', 
                                metrics =['accuracy'], callbacks = None):

        if self.model is None:
            raise TypeError('Model is NoneType object - not build')

        self.model.compile(optimizer = optimizer, 
                        loss=loss,
                        metrics = metrics)

        x_train, y_train = image_generator.train_array(batches_num = 100)
        x_test, y_test = image_generator.validation_array(batches_num = 10)
        
        history = self.model.fit(
            x_train,
            y_train,        
            epochs = epochs,
            validation_data = (x_test, y_test),
            callbacks = callbacks
        )

        return history


#importing libraries
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import AveragePooling2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Dropout
from keras.layers.core import Dense
from keras.layers import Flatten
from keras.layers import Input
from keras.models import Model
from keras.layers import concatenate
from keras import backend as K

class MiniGoogleNet:
	@staticmethod

	def conv_module(x, K, kX, kY, stride, chanDim, padding="same"):
		#define a CONV => BN => RELU pattern
		x = Conv2D(K, (kX, kY), strides=stride, padding=padding)(x)
		x = BatchNormalization(axis=chanDim)(x)
		x = Activation("relu")(x)

		return x

		#x: The input layer to the function.
		#K: The number of filters our CONV layer is going to learn.
		#kX and kY: The size of each of the K filters that will be learned.
		#stride: The stride of the CONV layer.
		#chanDim: The channel dimension, which is derived from either “channels last” or 
		#“channels first” ordering.
		#padding: The type of padding to be applied to the CONV lay

		@staticmethod
		def inception_module(x, numK1x1, numK3x3, chanDim):
			conv_1x1 = MiniGoogLeNet.conv_module(x, numK1x1, 1, 1, (1, 1), chanDim)
			conv_3x3 = MiniGoogLeNet.conv_module(x, numK3x3, 3, 3, (1, 1), chanDim)
			x = concatenate([conv_1x1, conv_3x3], axis=chanDim)

			return x

		@staticmethod
		def downsample_module(x, K, chanDim):
			conv_3x3 = MiniGoogLeNet.conv_module(x, K, 3, 3, (2, 2), chanDim, padding="valid")
			pool = MaxPooling2D((3, 3), strides=(2, 2))(x)
			x = concatenate([conv_3x3, pool], axis=chanDim)

			return x

		@staticmethod
		def build(width, height, depth, classes):
			#initialize the input shape to be "channel last" and channels dimension itself
			inputShape = (height, width, depth)
			chanDim = -1

			#if we are using "channel first", update the inpute shape and channel dimension
			if K.image_data_format() == "channels_first":
				inputShape = (depth, height, width)
				chanDim = 1

			#define the model input and first CONV module
			inputs = Input(shape=inputShape)
			x = MiniGoogLeNet.conv_module(inputs, 96, 3, 3, (1, 1), chanDim)
			
			#two Inception modules followed by a downsample module
			x = MiniGoogleNet.inception_module(x, 32, 32, chanDim)
			x = MiniGoogleNet.inception_module(x, 32, 48, chanDim)
			x = MiniGoogleNet.downsample_module(x, 80, chanDim)
			
			#four Inception module followed by a downsample module
			x = MiniGoogLeNet.inception_module(x, 112, 48, chanDim)
			x = MiniGoogLeNet.inception_module(x, 96, 64, chanDim)
			x = MiniGoogLeNet.inception_module(x, 80, 80, chanDim)
			x = MiniGoogLeNet.inception_module(x, 48, 96, chanDim)
			x = MiniGoogLeNet.downsample_module(x, 96, chanDim)

			#two Inception module followed by global POOL and dropout
			x = MiniGoogLeNet.inception_module(x, 176, 160, chanDim)
			x = MiniGoogLeNet.inception_module(x, 176, 160, chanDim)
			x = AveragePooling2D((7, 7))(x)
			x = Dropout(0.5)(x)

			#softmax classifier
			x = Flatten()(x)
			x = Dense(classes)(x)
			x = Activation("softmax")(x)

			#create the model
			model = Model(inputs, x, name="googlenet")

			#return the constructed network architecture
			return model
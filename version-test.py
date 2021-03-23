import tensorflow as tf
from tensorflow.python.client import device_lib

print("Tensorflow version: ", tf.__version__)

gpus = tf.config.list_physical_devices('GPU')
print("Is GPU Available: ", "True" if len(gpus) > 0 else "False" )

for gpu in gpus:
    print("Name:", gpu.name, "  Type:", gpu.device_type)

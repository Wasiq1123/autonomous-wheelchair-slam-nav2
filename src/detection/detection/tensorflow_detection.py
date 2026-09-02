import os
import rclpy
import numpy as np
import tensorflow as tf 
from rclpy.node import Node
from tensorflow import keras
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2

class Detection(Node):
    def __init__(self):
        super().__init__('detection')
        self.subscription = self.create_subscription(Image, '/camera/color/image_raw', self.image_callback, 10)
        self.cv_bridge = CvBridge()
        self.model = tf.keras.applications.resnet50.ResNet50(
            include_top=True,
            weights='imagenet',
            input_tensor=None,
            input_shape=None,
            pooling=None,
            classes=1000,
        )

    def image_callback(self, msg):
        cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8").astype(np.int8)
        image_tensor = tf.convert_to_tensor(cv_image)
        image_resized = tf.image.resize(image_tensor, (224, 224))
        image_batch = tf.expand_dims(image_resized, axis=0)
        image_batch = tf.keras.applications.resnet50.preprocess_input(image_batch)
        preds = self.model.predict(image_batch)
        decoded_preds = tf.keras.applications.imagenet_utils.decode_predictions(
            preds=preds,
            top=5
        )
        print(decoded_preds)

def main(args=None):
    rclpy.init(args=args)
    detection_node = Detection()
    rclpy.spin(detection_node)
    detection_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

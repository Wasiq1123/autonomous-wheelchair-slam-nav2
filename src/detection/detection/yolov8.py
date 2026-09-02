import os
from ultralytics import YOLO
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
        self.model_path = 'yolov8n.pt'
        if not os.path.exists(self.model_path):
            self.model = YOLO(weights=self.model_path)
        else:
            self.model = YOLO(self.model_path)

        self.cvbridge = CvBridge()

    def image_callback(self, msg):
        cv_image = self.cvbridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        results = self.model(cv_image)
        img=results[0].plot() 
        cv2.imshow('Detected Image', img)
        cv2.waitKey(10)

def main(args=None):
    rclpy.init(args=args)
    detection_node = Detection()
    rclpy.spin(detection_node)
    detection_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

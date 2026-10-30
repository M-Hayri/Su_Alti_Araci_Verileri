#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class DerinlikSensoru(Node):
    def __init__(self):
        super().__init__('derinlik_sensoru')
        
        K = 1
        self.frekans = float(K + 1)  # 2 Hz
        self.derinlik = 0.0
        self.son_komut = 0.0
        
        # Derinlik yayınlayan publisher
        self.publisher_ = self.create_publisher(Float32, '/derinlik', 10)
        
        # Motor komutunu dinleyen subscriber
        self.subscription = self.create_subscription(
            Float32,
            '/motor_komutu',
            self.motor_callback,
            10
        )
        
        # Timer (dt = 0.5 saniye)
        self.dt = 1.0 / self.frekans
        self.timer = self.create_timer(self.dt, self.timer_callback)
        self.get_logger().info('Dinamik Sensör Başlatıldı.')

    def motor_callback(self, msg):
        self.son_komut = msg.data

    def timer_callback(self):
        # Fiziksel Derinlik Değişimi: derinlik = derinlik + komut * dt
        self.derinlik += self.son_komut * self.dt
        
        # Denizaltı yüzeyin üstüne (derinlik < 0) çıkamaz
        if self.derinlik < 0.0:
            self.derinlik = 0.0

        # Sensör gürültüsü
        gurultu = random.uniform(-0.02, 0.02)
        olculen = self.derinlik + gurultu

        msg = Float32()
        msg.data = float(olculen)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikSensoru()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
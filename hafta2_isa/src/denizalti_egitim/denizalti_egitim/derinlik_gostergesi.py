#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DerinlikGostergesi(Node):
    def __init__(self):
        super().__init__('derinlik_gostergesi')
        
        # Öğrenci numarasının son hanesi
        K = 1
        
        # K = 1 için uyarı sınırı: 1.0 + (1 / 2) = 1.5m
        self.uyari_siniri = 1.0 + (K / 2.0)
        
        # /derinlik topic'ini dinleyen subscriber
        self.subscription = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_callback,
            10
        )
        self.get_logger().info('Derinlik gostergesi baslatildi.')

    def derinlik_callback(self, msg):
        derinlik = msg.data
        
        # Derinlik 1.5m sınırını geçerse UYARI verir
        if derinlik > self.uyari_siniri:
            self.get_logger().warn(f'UYARI: Derinlik siniri asildi! Derinlik: {derinlik:.2f} m')
        else:
            self.get_logger().info(f'Derinlik: {derinlik:.2f} m')

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikGostergesi()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
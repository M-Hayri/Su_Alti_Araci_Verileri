#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SuAltiDinleyiciDugumu(Node):
    def __init__(self):
        super().__init__('su_alti_dinleyici')
        self.subscription = self.create_subscription(
            String,
            'mezamortaDurumTopigi',
            self.listener_callback,
            10)
        self.get_logger().info('Mezamorta Dinleyici (Subscriber) Düğümü Başlatıldı ve Bekliyor...')

    def listener_callback(self, msg):
        # Kanaldan bir mesaj geldiğinde bu fonksiyon otomatik çalışır
        self.get_logger().info(f'>> Yakalanan Mesaj: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    su_alti_dinleyici = SuAltiDinleyiciDugumu()
    try:
        rclpy.spin(su_alti_dinleyici)
    except KeyboardInterrupt:
        pass

    su_alti_dinleyici.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

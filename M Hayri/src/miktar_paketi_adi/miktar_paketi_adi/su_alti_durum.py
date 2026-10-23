#!/usr/bin/env python3
import rclpy
from  rclpy.node import Node
from std_msgs.msg import String

class SuAltiDurumDugumu(Node):
	def __init__(self):
		super().__init__('su_alti_duru')

		self.publisher_ = self.create_publisher(String, 'mezamortaDurumTopigi',10)
		self.get_logger().info('Mezamorta Yayıncı (Publisher) Düğümü Başlatıldı!')
		self.timer = self.create_timer(1.0, self.timer_callback)
		self.i = 0

	def timer_callback(self):
		msg = String()
		msg.data = f'Mezamorta Durum Raporu - Sure {self.i}'

		self.publisher_.publish(msg)
		self.get_logger().info(f'yayınlanın: "{msg.data}"')
		self.i += 1


def main(args=None):
    rclpy.init(args=args)
    su_alti_durum = SuAltiDurumDugumu()

    try:
        rclpy.spin(su_alti_durum)
    except KeyboardInterrupt:
        pass

    su_alti_durum.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

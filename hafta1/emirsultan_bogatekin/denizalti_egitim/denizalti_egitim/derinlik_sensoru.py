
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


K = 28


class DerinlikSensoru(Node):
    def __init__(self):
        super().__init__('derinlik_sensoru')

        self.derinlik = 0.0
        self.motor_komutu = 0.0

        self.publisher = self.create_publisher(
            Float32, '/derinlik', 10
        )

        self.subscription = self.create_subscription(
            Float32,
            '/motor_komutu',
            self.motor_komutu_al,
            10
        )

        self.dt = 1.0 / (K + 1)
        self.timer = self.create_timer(
            self.dt, self.guncelle
        )

        self.get_logger().info('Sahte derinlik sensörü başlatıldı.')

    def motor_komutu_al(self, mesaj):
        self.motor_komutu = mesaj.data

    def guncelle(self):
        
        self.derinlik += self.motor_komutu * self.dt

        
        self.derinlik = max(0.0, self.derinlik)

        mesaj = Float32()
        gurultu = random.uniform(-0.05, 0.05)
        mesaj.data = float(max(0.0, self.derinlik + gurultu))

        self.publisher.publish(mesaj)


def main(args=None):
    rclpy.init(args=args)
    node = DerinlikSensoru()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

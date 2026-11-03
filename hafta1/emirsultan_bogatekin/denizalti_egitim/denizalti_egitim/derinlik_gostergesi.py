import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class DerinlikGostergesi(Node):

    def __init__(self):
        super().__init__('derinlik_gostergesi')

        self.subscription = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_callback,
            10
        )

    def derinlik_callback(self, msg):
        derinlik = msg.data

        self.get_logger().info(
            f'Derinlik: {derinlik:.2f} m'
        )

        if derinlik > 15.0:
            self.get_logger().warn(
                'UYARI: Derinlik siniri asildi!'
            )


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

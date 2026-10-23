import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DerinlikGostergesi(Node):
    def __init__(self):
        super().__init__('derinlik_gostergesi')
        
      
        self.subscription = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_dinle,
            10
        )
        
        self.K = 9
        self.sinir_derinlik = 1.0 + (self.K / 2.0)
        self.get_logger().info(f'Gosterge hazir. Uyari siniri: {self.sinir_derinlik:.2f} m')

    def derinlik_dinle(self, msg):
        derinlik = msg.data
        self.get_logger().info(f'Derinlik: {derinlik:.2f} m')
        
        if derinlik > self.sinir_derinlik:
            self.get_logger().warn('UYARI: Derinlik siniri asildi!')

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikGostergesi()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
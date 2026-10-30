import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DerinlikHesaplayici(Node):
    def __init__(self):
        super().__init__('derinlik_hesaplayici')
        self.declare_parameter('su_yogunlugu', 1000.0)
        
        self.sub_basinc = self.create_subscription(
            Float32, '/basinc', self.basinc_callback, 10)
        self.pub_derinlik = self.create_publisher(Float32, '/derinlik', 10)

    def basinc_callback(self, msg):
        rho = self.get_parameter('su_yogunlugu').get_parameter_value().double_value
        g = 9.81
        p_ortam = 101325.0
        
        derinlik = (msg.data - p_ortam) / (rho * g)
        if derinlik < 0.0:
            derinlik = 0.0

        out_msg = Float32()
        out_msg.data = float(derinlik)
        self.pub_derinlik.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikHesaplayici()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
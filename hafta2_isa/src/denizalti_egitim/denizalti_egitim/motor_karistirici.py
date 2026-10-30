import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Float32MultiArray

class MotorKaristirici(Node):
    def __init__(self):
        super().__init__('motor_karistirici')
        
        self.dikey_komut = 0.0
        self.donus_komutu = 0.0
        
        self.son_dikey_zaman = self.get_clock().now()
        self.son_donus_zaman = self.get_clock().now()

        self.sub_dikey = self.create_subscription(
            Float32, '/dikey_komut', self.dikey_cb, 10)
        self.sub_donus = self.create_subscription(
            Float32, '/donus_komutu', self.donus_cb, 10)
        
        self.pub_itici = self.create_publisher(Float32MultiArray, '/itici_komutlari', 10)
        self.timer = self.create_timer(0.1, self.yayinla)

    def dikey_cb(self, msg):
        self.dikey_komut = msg.data
        self.son_dikey_zaman = self.get_clock().now()

    def donus_cb(self, msg):
        self.donus_komutu = msg.data
        self.son_donus_zaman = self.get_clock().now()

    def yayinla(self):
        simdi = self.get_clock().now()
        
        if (simdi - self.son_dikey_zaman).nanoseconds / 1e9 > 1.0:
            if self.dikey_komut != 0.0:
                self.get_logger().error("KOMUT KAYIP: dikey")
            self.dikey_komut = 0.0

        if (simdi - self.son_donus_zaman).nanoseconds / 1e9 > 1.0:
            if self.donus_komutu != 0.0:
                self.get_logger().error("KOMUT KAYIP: donus")
            self.donus_komutu = 0.0

        msg = Float32MultiArray()
        msg.data = [
            float(self.donus_komutu),
            float(self.donus_komutu),
            float(self.dikey_komut),
            float(self.dikey_komut)
        ]
        self.pub_itici.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MotorKaristirici()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class YonKontrolcu(Node):
    def __init__(self):
        super().__init__('yon_kontrolcu')
        self.declare_parameter('kp_yon', 0.02)

        self.hedef_yon = 0.0
        self.mevcut_yon = 0.0

        self.sub_hedef = self.create_subscription(
            Float32, '/hedef_yon', self.hedef_callback, 10)
        self.sub_yon = self.create_subscription(
            Float32, '/yon_acisi', self.yon_callback, 10)
        
        self.pub_donus = self.create_publisher(Float32, '/donus_komutu', 10)
        self.timer = self.create_timer(0.1, self.kontrol_dongusu)

    def hedef_callback(self, msg):
        self.hedef_yon = msg.data

    def yon_callback(self, msg):
        self.mevcut_yon = msg.data

    def kontrol_dongusu(self):
        hata = self.hedef_yon - self.mevcut_yon
        hata = (hata + 180.0) % 360.0 - 180.0 # En kısa yol dönüşü

        kp = self.get_parameter('kp_yon').value
        u = kp * hata
        u = max(min(u, 0.5), -0.5)

        msg = Float32()
        msg.data = float(u)
        self.pub_donus.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = YonKontrolcu()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

class DerinlikKontrolcu(Node):

    def __init__(self):
        super().__init__('derinlik_kontrolcu')

        self.mevcut_derinlik = 0.0
        self.hedef_derinlik = 0.0

        # Soru 3.4: Geç katılan düğümler (late-joining) için TRANSIENT_LOCAL QoS profili
        qos_profile = QoSProfile(
            depth=10,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )

        # Derinlik sensör verisini dinleyen abonelik
        self.sub_derinlik = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_cb,
            10
        )

        # Hedef derinlik verisini TRANSIENT_LOCAL profili ile dinleyen abonelik
        self.sub_hedef = self.create_subscription(
            Float32,
            '/hedef_derinlik',
            self.hedef_cb,
            qos_profile
        )

        # Derinlik kontrol sinyalini yayınlayan publisher
        self.pub_derinlik_kontrol = self.create_publisher(
            Float32,
            '/derinlik_kontrol',
            10
        )

        # Kontrol döngüsü (10 Hz)
        self.timer = self.create_timer(0.1, self.kontrol_dongusu)

    def derinlik_cb(self, msg):
        self.mevcut_derinlik = msg.data

    def hedef_cb(self, msg):
        self.hedef_derinlik = msg.data

    def kontrol_dongusu(self):
        # Basit P (Oransal) Kontrolcü
        hata = self.hedef_derinlik - self.mevcut_derinlik
        kp = 1.0  # Oransal kazanç
        u = kp * hata

        msg = Float32()
        msg.data = float(u)
        self.pub_derinlik_kontrol.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikKontrolcu()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

class DerinlikKontrolcu(Node):
    def __init__(self):
        super().__init__('derinlik_kontrolcu')
        self.declare_parameter('kp_derinlik', 1.0)
        self.declare_parameter('ki_derinlik', 0.2)
        self.declare_parameter('integral_sinir', 1.0)
        self.declare_parameter('max_izinli_derinlik', 3.5)

        self.hedef_derinlik = 0.0
        self.mevcut_derinlik = 0.0
        self.integral = 0.0
        self.son_zaman = self.get_clock().now()
        self.son_derinlik_zaman = self.get_clock().now()

        self.sub_hedef = self.create_subscription(
            Float32, '/hedef_derinlik', self.hedef_callback, 10)
        self.sub_derinlik = self.create_subscription(
            Float32, '/derinlik', self.derinlik_callback, 10)
        
        self.pub_dikey = self.create_publisher(Float32, '/dikey_komut', 10)
        self.timer = self.create_timer(0.1, self.kontrol_dongusu)
        self.add_on_set_parameters_callback(self.param_callback)

    def param_callback(self, params):
        for param in params:
            if param.name in ['kp_derinlik', 'ki_derinlik', 'integral_sinir'] and param.value < 0:
                return SetParametersResult(successful=False, reason=f"{param.name} negatif olamaz!")
        return SetParametersResult(successful=True)

    def hedef_callback(self, msg):
        max_d = self.get_parameter('max_izinli_derinlik').value
        if msg.data > max_d:
            self.get_logger().warn(f"Hedef derinlik sınır aşıldı! {max_d}m 'ye çekildi.")
            self.hedef_derinlik = max_d
        elif msg.data < 0.0:
            self.hedef_derinlik = 0.0
        else:
            self.hedef_derinlik = msg.data

    def derinlik_callback(self, msg):
        self.mevcut_derinlik = msg.data
        self.son_derinlik_zaman = self.get_clock().now()

    def kontrol_dongusu(self):
        simdi = self.get_clock().now()
        dt = (simdi - self.son_zaman).nanoseconds / 1e9
        self.son_zaman = simdi

        if (simdi - self.son_derinlik_zaman).nanoseconds / 1e9 > 1.0:
            self.get_logger().error("SENSÖR KAYIP! Dikey komut = 0")
            msg = Float32()
            msg.data = 0.0
            self.pub_dikey.publish(msg)
            return

        hata = self.hedef_derinlik - self.mevcut_derinlik
        
        kp = self.get_parameter('kp_derinlik').value
        ki = self.get_parameter('ki_derinlik').value
        i_limit = self.get_parameter('integral_sinir').value

        self.integral += hata * dt
        self.integral = max(min(self.integral, i_limit), -i_limit)

        u = (kp * hata) + (ki * self.integral)
        u = max(min(u, 0.5), -0.5)

        msg = Float32()
        msg.data = float(u)
        self.pub_dikey.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikKontrolcu()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
import rclpy
from rclpy.node import Node
from denizalti_msgs.msg import MotorKomut, DenizaltiDurum

class AracSimulasyonu(Node):
    def __init__(self):
        super().__init__('arac_simulasyonu')
        
        self.declare_parameter('frekans', 2.0)
        self.declare_parameter('sephiye_hizi', 0.06)
        self.declare_parameter('baslangic_yonu', 0.0)
        self.declare_parameter('su_yogunlugu', 1000.0)

        self.frekans = self.get_parameter('frekans').value
        self.sephiye_hizi = self.get_parameter('sephiye_hizi').value
        self.su_yogunlugu = self.get_parameter('su_yogunlugu').value

        self.derinlik = 0.0
        self.yon = self.get_parameter('baslangic_yonu').value
        self.dikey_hiz = 0.0
        self.donus_hizi = 0.0

        self.sub = self.create_subscription(MotorKomut, '/denizalti/motor_komut', self.motor_cb, 10)
        self.pub = self.create_publisher(DenizaltiDurum, '/denizalti/durum', 10)

        timer_period = 1.0 / self.frekans
        self.timer = self.create_timer(timer_period, self.loop)

    def motor_cb(self, msg):
        self.donus_hizi = (msg.sag_motor - msg.sol_motor) * 0.01
        net_dikey = (msg.dikey_on_motor + msg.dikey_arka_motor) / 2.0
        self.dikey_hiz = (net_dikey * 0.05) + self.sephiye_hizi

    def loop(self):
        self.derinlik = max(0.0, self.derinlik + (self.dikey_hiz / self.frekans))
        self.yon = (self.yon + (self.donus_hizi / self.frekans)) % 360.0

        msg = DenizaltiDurum()
        msg.derinlik = float(self.derinlik)
        msg.yon = float(self.yon)
        msg.basinc = float(101325.0 + (self.su_yogunlugu * 9.81 * self.derinlik))
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AracSimulasyonu()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
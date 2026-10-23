#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from std_srvs.srv import Trigger

class DerinlikKontrolcu(Node):
    def __init__(self):
        super().__init__('derinlik_kontrolcu')
        
        K = 1
        
        # ROS Parametreleri (Varsayılan değerler)
        # Hedef Derinlik = 1.0 + (1 / 5.0) = 1.2 m
        self.declare_parameter('hedef_derinlik', 1.0 + (K / 5.0))
        self.declare_parameter('kp', 0.5)
        
        # Motor komutu yayınlayıcı
        self.cmd_pub = self.create_publisher(Float32, '/motor_komutu', 10)
        
        # Derinlik sensörü abonesi
        self.subscription = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_callback,
            10
        )
        
        # Acil Yüzey Servisi (/acil_yuzey)
        self.srv = self.create_service(Trigger, '/acil_yuzey', self.acil_yuzey_callback)
        
        self.get_logger().info('Derinlik Kontrolcü Başlatıldı.')

    def derinlik_callback(self, msg):
        mevcut_derinlik = msg.data
        
        # Parametreleri oku (Terminalden değiştirilirse anında güncellenir)
        hedef = self.get_parameter('hedef_derinlik').get_parameter_value().double_value
        kp = self.get_parameter('kp').get_parameter_value().double_value
        
        # Hata Hesabı: e(t) = Hedef - Mevcut
        hata = hedef - mevcut_derinlik
        
        # P Kontrol Formülü: u(t) = Kp * e(t)
        motor_komutu = kp * hata
        
        # Komutu yayınla
        cmd_msg = Float32()
        cmd_msg.data = float(motor_komutu)
        self.cmd_pub.publish(cmd_msg)
        
        self.get_logger().info(f'Hedef: {hedef:.2f}m | Derinlik: {mevcut_derinlik:.2f}m | Motor Komutu: {motor_komutu:.2f}')

    def acil_yuzey_callback(self, request, response):
        # Hedef derinliği anında 0.0 yap
        param = rclpy.parameter.Parameter('hedef_derinlik', rclpy.Parameter.Type.DOUBLE, 0.0)
        self.set_parameters([param])
        
        response.success = True
        response.message = 'ACIL DURUM: Hedef derinlik 0.0m yapildi, yüzeye cikiliyor!'
        self.get_logger().warn(response.message)
        return response

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikKontrolcu()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
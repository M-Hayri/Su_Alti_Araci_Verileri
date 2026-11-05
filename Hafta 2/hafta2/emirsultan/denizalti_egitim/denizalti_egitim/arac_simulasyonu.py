#!/usr/bin/env python3
"""
Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama
Düğüm: arac_simulasyonu
Fiziksel sualtı aracı hareket ve hidrostatik simülatörü.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Float32MultiArray

try:
    from denizalti_msgs.msg import MotorKomut, DenizaltiDurum
    DENIZALTI_MSGS_MEVCUT = True
except ImportError:
    DENIZALTI_MSGS_MEVCUT = False


class AracSimulasyonu(Node):
    def __init__(self):
        super().__init__('arac_simulasyonu')
        
        self.declare_parameter('frekans', 9.0)
        self.declare_parameter('sephiye_hizi', 0.13)
        self.declare_parameter('baslangic_yonu', 0.0)
        self.declare_parameter('su_yogunlugu', 1000.0)

        self.frekans = float(self.get_parameter('frekans').value)
        self.sephiye_hizi = float(self.get_parameter('sephiye_hizi').value)
        self.su_yogunlugu = float(self.get_parameter('su_yogunlugu').value)

        self.derinlik = 0.0
        self.yon = float(self.get_parameter('baslangic_yonu').value)
        self.dikey_hiz = 0.0
        self.donus_hizi = 0.0

        # Motor komutlarını dinle (MotorKomut ve Float32MultiArray)
        if DENIZALTI_MSGS_MEVCUT:
            self.sub = self.create_subscription(MotorKomut, '/denizalti/motor_komut', self.motor_cb, 10)
            self.pub = self.create_publisher(DenizaltiDurum, '/denizalti/durum', 10)

        self.sub_dizi = self.create_subscription(Float32MultiArray, '/itici_komutlari', self.itici_dizi_cb, 10)

        # Standart başlık yayıncıları
        self.pub_basinc = self.create_publisher(Float32, '/basinc', 10)
        self.pub_yon = self.create_publisher(Float32, '/yon_acisi', 10)
        self.pub_gercek_derinlik = self.create_publisher(Float32, '/gercek_derinlik', 10)

        timer_period = 1.0 / self.frekans
        self.timer = self.create_timer(timer_period, self.loop)
        self.get_logger().info(f'Araç Simülasyonu başlatıldı (Frekans: {self.frekans} Hz, Sephiye: {self.sephiye_hizi} m/s).')

    def motor_cb(self, msg):
        donus = (msg.sag_motor - msg.sol_motor) / 2.0
        self.donus_hizi = donus * 60.0
        net_dikey = (msg.dikey_on_motor + msg.dikey_arka_motor) / 2.0
        # Pozitif komut aşağı iter (+net_dikey), sephiye yukarı çeker (-sephiye_hizi)
        self.dikey_hiz = net_dikey - self.sephiye_hizi

    def itici_dizi_cb(self, msg):
        # [donus, donus, dikey, dikey]
        if len(msg.data) >= 4:
            donus = msg.data[0]
            dikey = msg.data[2]
            self.donus_hizi = donus * 60.0
            # Pozitif komut aşağı iter (+dikey), sephiye yukarı çeker (-sephiye_hizi)
            self.dikey_hiz = dikey - self.sephiye_hizi

    def loop(self):
        # Fiziksel derinlik ve rota entegrasyonu
        self.derinlik = max(0.0, self.derinlik + (self.dikey_hiz / self.frekans))
        self.yon = (self.yon + (self.donus_hizi / self.frekans)) % 360.0

        basinc_degeri = float(101325.0 + (self.su_yogunlugu * 9.81 * self.derinlik))

        if DENIZALTI_MSGS_MEVCUT:
            msg = DenizaltiDurum()
            msg.derinlik = float(self.derinlik)
            msg.yon = float(self.yon)
            msg.basinc = basinc_degeri
            self.pub.publish(msg)

        # /basinc, /yon_acisi ve /gercek_derinlik başlıklarına yayın
        p_msg = Float32()
        p_msg.data = basinc_degeri
        self.pub_basinc.publish(p_msg)

        y_msg = Float32()
        y_msg.data = float(self.yon)
        self.pub_yon.publish(y_msg)

        d_msg = Float32()
        d_msg.data = float(self.derinlik)
        self.pub_gercek_derinlik.publish(d_msg)


def main(args=None):
    rclpy.init(args=args)
    node = AracSimulasyonu()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random

class SuAltiSensorSimulator(Node):
    def __init__(self):
        super().__init__('su_alti_sensor_sim')
        
        # Sensör verilerini yayınlayacağımız kanal
        self.publisher_ = self.create_publisher(String, 'mavi_golge_sensor_verileri', 10)
        
        # Her 1.5 saniyede bir sensör verisi üretelim
        self.timer = self.create_timer(1.5, self.sensor_callback)
        
        # Başlangıç değerleri (Su altı simülasyonu)
        self.derinlik = 10.0  # metre
        self.sicaklik = 18.5  # Santigrat
        
        self.get_logger().info('Mavi Gölge Su Altı Sensör Simülatörü Başlatıldı...')

    def sensor_callback(self):
        # Gerçekçi dalgalanmalar ekleyelim (gürültü simülasyonu)
        self.derinlik += random.uniform(-0.3, 0.4)
        self.sicaklik += random.uniform(-0.1, 0.1)
        
        # Değerlerin mantıklı sınırda kalmasını sağlayalım
        if self.derinlik < 0: 
            self.derinlik = 0.0

        # Veriyi birleştirip mesaj haline getirelim
        veri_metni = (f"Derinlik: {self.derinlik:.2f} m | "
                      f"Basınç: {(1.0 + self.derinlik/10.0):.2f} atm | "
                      f"Sıcaklık: {self.sicaklik:.2f} C")
        
        msg = String()
        msg.data = veri_metni
        
        self.publisher_.publish(msg)
        self.get_logger().info(f'Yayınlanan Sensör Verisi -> {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = SuAltiSensorSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

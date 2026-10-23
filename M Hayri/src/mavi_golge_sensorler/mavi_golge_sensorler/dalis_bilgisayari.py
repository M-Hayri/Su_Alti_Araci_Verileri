#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DalisBilgisayari(Node):
    def __init__(self):
        super().__init__('dalis_bilgisayari')
        
        # Sensör kanalını dinliyoruz
        self.subscription = self.create_subscription(
            String,
            'mavi_golge_sensor_verileri',
            self.listener_callback,
            10)
            
        self.get_logger().info('Mavi Gölge Dalış Bilgisayarı (Kontrol Paneli) Aktif...')

    def listener_callback(self, msg):
        self.get_logger().info(f'[KONTROL PANELİ] Gelen Veri -> {msg.data}')
        
        # Örnek mantık: Derinlik kelimesini yakalayıp basit bir kontrol yapabiliriz
        if "Derinlik:" in msg.data:
            try:
                # Metin içinden derinlik değerini ayıklama simülasyonu
                parcalar = msg.data.split('|')
                derinlik_str = parcalar[0].replace('Derinlik:', '').replace('m', '').strip()
                derinlik_val = float(derinlik_str)
                
                if derinlik_val > 15.0:
                    self.get_logger().warn('*** UYARI: Mavi Gölge Güvenli Derinlik Sınırını Aştı! ***')
            except Exception:
                pass

def main(args=None):
    rclpy.init(args=args)
    node = DalisBilgisayari()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

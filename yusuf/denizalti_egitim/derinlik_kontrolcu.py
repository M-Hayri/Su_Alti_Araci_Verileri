import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from std_srvs.srv import Trigger

class DerinlikKontrolcu(Node):
    def __init__(self):
        super().__init__('derinlik_kontrolcu')
        
        # Parametreler (K=9 için başlangıç hedef: 1 + 9/5 = 2.8 m)
        self.declare_parameter('hedef_derinlik', 2.8)
        self.declare_parameter('kp', 0.5)
        
        # /derinlik abonesi
        self.sub_derinlik = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_callback,
            10
        )
        
        # /motor_komutu yayıncısı
        self.pub_motor = self.create_publisher(Float32, '/motor_komutu', 10)
        
        # /acil_yuzey servisi
        self.srv_acil = self.create_service(
            Trigger,
            '/acil_yuzey',
            self.acil_yuzey_callback
        )
        
        self.get_logger().info('Derinlik Kontrolcu baslatildi.')

    def acil_yuzey_callback(self, request, response):
        # Parametreyi 0 yap
        param = rclpy.parameter.Parameter(
            'hedef_derinlik',
            rclpy.Parameter.Type.DOUBLE,
            0.0
        )
        self.set_parameters([param])
        self.get_logger().warn('ACİL YÜZEYE ÇIKIŞ!')
        response.success = True
        response.message = 'Acil yuzeye cikis baslatildi (hedef = 0.0 m)'
        return response

    def derinlik_callback(self, msg):
        olculen_derinlik = msg.data
        
        # Parametreleri dinamik oku
        hedef_derinlik = self.get_parameter('hedef_derinlik').value
        kp = self.get_parameter('kp').value
        
        # P Kontrol: hata = hedef - ölçülen, komut = Kp * hata
        hata = hedef_derinlik - olculen_derinlik
        komut = kp * hata
        
        # Komutu [-0.5, +0.5] arasına sınırla
        komut = max(-0.5, min(0.5, komut))
        
        # Motor komutunu yayınla
        motor_msg = Float32()
        motor_msg.data = float(komut)
        self.pub_motor.publish(motor_msg)
        
        self.get_logger().info(
            f'Derinlik: {olculen_derinlik:.2f} m | Hata: {hata:.2f} m | Komut: {komut:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikKontrolcu()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
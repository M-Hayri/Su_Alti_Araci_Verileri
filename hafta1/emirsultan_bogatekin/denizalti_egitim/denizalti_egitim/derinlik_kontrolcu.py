
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import Float32
from std_srvs.srv import Trigger


K = 28


class DerinlikKontrolcu(Node):
    def __init__(self):
        super().__init__('derinlik_kontrolcu')

        self.declare_parameter('hedef_derinlik', 1.0 + K / 5.0)
        self.declare_parameter('kp', 0.5)

        
        self.acil_mod = False

        self.publisher = self.create_publisher(
            Float32, '/motor_komutu', 10
        )

        self.subscription = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_alindi,
            10
        )

        self.acil_service = self.create_service(
            Trigger,
            '/acil_yuzey',
            self.acil_yuzey_callback
        )

        self.devam_service = self.create_service(
            Trigger,
            '/devam',
            self.devam_callback
        )

        self.get_logger().info('Derinlik kontrolcüsü başlatıldı.')

    def derinlik_alindi(self, mesaj):
        derinlik = float(mesaj.data)

        if self.acil_mod:
            
            if derinlik > 0.05:
                komut = -0.5
            else:
                komut = 0.0

            self.motor_komutu_yayinla(komut)

            self.get_logger().warn(
                f'ACİL MOD | Derinlik: {derinlik:.2f} m '
                f'| Komut: {komut:.2f}'
            )
            return

        hedef = float(
            self.get_parameter('hedef_derinlik').value
        )
        kp = float(self.get_parameter('kp').value)

        hata = hedef - derinlik
        komut = kp * hata
        komut = max(-0.5, min(0.5, komut))

        self.motor_komutu_yayinla(komut)

        self.get_logger().info(
            f'Derinlik: {derinlik:.2f} m | '
            f'Hata: {hata:.2f} m | '
            f'Komut: {komut:.2f}'
        )

    def motor_komutu_yayinla(self, komut):
        mesaj = Float32()
        mesaj.data = float(komut)
        self.publisher.publish(mesaj)

    def acil_yuzey_callback(self, request, response):
        self.acil_mod = True

        
        self.set_parameters([
            Parameter('hedef_derinlik', value=0.0)
        ])

        self.get_logger().error('ACİL YÜZEYE ÇIKIŞ: ACİL MOD AKTİF')

        response.success = True
        response.message = 'Acil mod aktif. Yüzeye çıkılıyor.'
        return response

    def devam_callback(self, request, response):
        self.acil_mod = False

        self.get_logger().info(
            'DEVAM: Normal derinlik kontrolü yeniden etkin.'
        )

        response.success = True
        response.message = 'Normal kontrol modu etkinleştirildi.'
        return response


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

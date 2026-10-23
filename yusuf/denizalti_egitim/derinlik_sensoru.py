import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DerinlikSensoru(Node):
    def __init__(self):
        super().__init__('derinlik_sensoru')
        
        # /derinlik yayıncısı
        self.publisher_ = self.create_publisher(Float32, '/derinlik', 10)
        
        # /motor_komutu dinleyicisi
        self.subscription = self.create_subscription(
            Float32,
            '/motor_komutu',
            self.motor_komutu_callback,
            10
        )
        
        self.derinlik = 0.0      # Yüzeyde başla (0 m)
        self.son_komut = 0.0     # Başlangıçta motor komutu yok
        
        # 10 Hz frekans (dt = 0.1 saniye)
        self.dt = 0.1
        self.timer = self.create_timer(self.dt, self.timer_callback)
        self.get_logger().info('Guncel Derinlik Sensoru baslatildi.')

    def motor_komutu_callback(self, msg):
        self.son_komut = msg.data

    def timer_callback(self):
        # derinlik = derinlik + komut * dt
        self.derinlik += self.son_komut * self.dt
        
        # Derinlik 0'ın altına düşemez (yüzey sınırı)
        if self.derinlik < 0.0:
            self.derinlik = 0.0
            
        msg = Float32()
        msg.data = float(self.derinlik)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DerinlikSensoru()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
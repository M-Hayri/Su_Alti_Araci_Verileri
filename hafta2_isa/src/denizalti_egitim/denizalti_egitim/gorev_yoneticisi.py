import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String
from std_srvs.srv import Trigger
from rcl_interfaces.msg import SetParametersResult
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

class GorevYoneticisi(Node):
    def __init__(self):
        super().__init__('gorev_yoneticisi')
        self.declare_parameter('dalis_derinligi', 1.2)
        self.declare_parameter('donus_yonu', 0.0)
        self.declare_parameter('max_izinli_derinlik', 3.5)

        self.durum = "BASLA"
        self.mevcut_derinlik = 0.0
        self.mevcut_yon = 0.0
        self.ilk_yon = None
        
        self.durum_baslangic = self.get_clock().now()
        self.sart_baslangic = None

        # Soru 3.4: Geç kalan node'lar için TRANSIENT_LOCAL QoS profili
        qos_profile = QoSProfile(
            depth=10,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )

        self.sub_derinlik = self.create_subscription(Float32, '/derinlik', self.derinlik_cb, 10)
        self.sub_yon = self.create_subscription(Float32, '/yon_acisi', self.yon_cb, 10)

        # QoS profili hedefler için publisher'lara eklendi
        self.pub_hedef_derinlik = self.create_publisher(Float32, '/hedef_derinlik', qos_profile)
        self.pub_hedef_yon = self.create_publisher(Float32, '/hedef_yon', qos_profile)
        self.pub_durum = self.create_publisher(String, '/gorev_durumu', 10)

        self.srv_acil = self.create_service(Trigger, '/acil_yuzey', self.acil_yuzey_cb)
        self.srv_devam = self.create_service(Trigger, '/devam', self.devam_cb)

        self.timer = self.create_timer(0.5, self.yayinla_ve_kontrol)
        self.add_on_set_parameters_callback(self.param_callback)

    def param_callback(self, params):
        max_d = self.get_parameter('max_izinli_derinlik').value
        for p in params:
            if p.name == 'dalis_derinligi' and not (0.0 <= p.value <= max_d):
                return SetParametersResult(successful=False, reason="Geçersiz dalış derinliği!")
            if p.name == 'donus_yonu' and not (0.0 <= p.value <= 360.0):
                return SetParametersResult(successful=False, reason="Dönüş yönü 0-360 arası olmalı!")
        return SetParametersResult(successful=True)

    def acil_yuzey_cb(self, request, response):
        self.durum_degistir("ACIL")
        response.success = True
        response.message = "Acil durum başlatıldı! Yüzeye çıkılıyor."
        return response

    def devam_cb(self, request, response):
        if self.durum == "ACIL":
            self.durum_degistir("DAL")
            response.success = True
            response.message = "Görev DAL durumundan devam ediyor."
        else:
            response.success = False
            response.message = "Cihaz ACIL durumunda değil!"
        return response

    def derinlik_cb(self, msg):
        self.mevcut_derinlik = msg.data

    def yon_cb(self, msg):
        self.mevcut_yon = msg.data
        if self.ilk_yon is None:
            self.ilk_yon = msg.data
            self.hedefleri_yayinla()

    def hedefleri_yayinla(self):
        if self.ilk_yon is None:
            return

        d_target_param = self.get_parameter('dalis_derinligi').value
        y_target_param = self.get_parameter('donus_yonu').value

        target_d = 0.0
        target_y = self.ilk_yon

        if self.durum in ["BASLA"]:
            target_d = 0.0
            target_y = self.ilk_yon
        elif self.durum in ["DAL"]:
            target_d = d_target_param
            target_y = self.ilk_yon
        elif self.durum in ["DON", "BEKLE"]:
            target_d = d_target_param
            target_y = y_target_param
        elif self.durum in ["YUZEY", "BITTI"]:
            target_d = 0.0
            target_y = y_target_param
        elif self.durum == "ACIL":
            target_d = 0.0
            target_y = self.mevcut_yon

        msg_d = Float32()
        msg_d.data = float(target_d)
        self.pub_hedef_derinlik.publish(msg_d)

        msg_y = Float32()
        msg_y.data = float(target_y)
        self.pub_hedef_yon.publish(msg_y)

    def durum_degistir(self, yeni_durum):
        self.durum = yeni_durum
        self.durum_baslangic = self.get_clock().now()
        self.sart_baslangic = None
        self.get_logger().info(f"YENİ DURUM: {yeni_durum}")
        
        d_msg = String()
        d_msg.data = yeni_durum
        self.pub_durum.publish(d_msg)

        self.hedefleri_yayinla()

    def yayinla_ve_kontrol(self):
        if self.ilk_yon is None:
            return

        simdi = self.get_clock().now()
        gecen_sure = (simdi - self.durum_baslangic).nanoseconds / 1e9

        d_target_param = self.get_parameter('dalis_derinligi').value
        y_target_param = self.get_parameter('donus_yonu').value

        if self.durum == "BASLA":
            if gecen_sure >= 3.0:
                self.durum_degistir("DAL")

        elif self.durum == "DAL":
            if abs(self.mevcut_derinlik - d_target_param) < 0.1:
                if self.sart_baslangic is None:
                    self.sart_baslangic = simdi
                elif (simdi - self.sart_baslangic).nanoseconds / 1e9 >= 3.0:
                    self.durum_degistir("DON")
            else:
                self.sart_baslangic = None

        elif self.durum == "DON":
            hata = (y_target_param - self.mevcut_yon + 180.0) % 360.0 - 180.0
            if abs(hata) < 5.0:
                if self.sart_baslangic is None:
                    self.sart_baslangic = simdi
                elif (simdi - self.sart_baslangic).nanoseconds / 1e9 >= 3.0:
                    self.durum_degistir("BEKLE")
            else:
                self.sart_baslangic = None

        elif self.durum == "BEKLE":
            if gecen_sure >= 10.0:
                self.durum_degistir("YUZEY")

        elif self.durum == "YUZEY":
            if self.mevcut_derinlik < 0.1:
                self.durum_degistir("BITTI")

def main(args=None):
    rclpy.init(args=args)
    node = GorevYoneticisi()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
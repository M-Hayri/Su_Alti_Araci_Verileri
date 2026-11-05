#!/usr/bin/env python3
"""
Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama
Düğüm: derinlik_kontrolcu
Yazar: Emir Sultan (K=8)

Açıklama:
Hedef derinlik bilgisi ile anlık derinlik ölçümünü kıyaslayarak oransal-integral (PI)
denetim sinyali üretir (/dikey_komut). Anti-windup mekanizması, sensör zaman aşımı
(watchdog) ve parametre güvenlik kısıtları barındırır.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Float32


class DerinlikPIDDenetleyici(Node):
    """
    Dikey eksende derinlik koruma ve hedef derinliğe dalış sağlayan PI kontrolcü.
    """

    def __init__(self):
        super().__init__('derinlik_kontrolcu')

        
        self.declare_parameter('kp_derinlik', 1.0)
        self.declare_parameter('ki_derinlik', 0.2)
        self.declare_parameter('integral_sinir', 1.0)
        self.declare_parameter('max_izinli_derinlik', 7.0)  # K=8 için 3 + 8/2 = 7.0m

       
        self._hedef_derinlik = 0.0
        self._guncel_derinlik = 0.0
        self._integral_toplami = 0.0
        self._sensor_kayip_uyarildi = False

        simdi = self.get_clock().now()
        self._son_dongu_zamani = simdi
        self._son_derinlik_zamani = simdi

        
        kalici_qos = QoSProfile(
            depth=10,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )

        
        self.abone_hedef = self.create_subscription(
            Float32,
            '/hedef_derinlik',
            self.hedef_derinlik_alindi,
            kalici_qos
        )

        
        self.abone_derinlik = self.create_subscription(
            Float32,
            '/derinlik',
            self.derinlik_geribesleme_alindi,
            10
        )

        
        self.yayinici_dikey_komut = self.create_publisher(
            Float32,
            '/dikey_komut',
            10
        )

        
        self.denetim_zamani = self.create_timer(0.1, self.denetim_dongusu)

        
        self.add_on_set_parameters_callback(self.parametre_gecerlilik_denetimi)

        self.get_logger().info('Derinlik PID Kontrolcüsü başarıyla başlatıldı.')

    def parametre_gecerlilik_denetimi(self, parametre_listesi):
        """Çalışma zamanında parametre güncellemelerini filtreleyerek negatif değerleri engeller."""
        for param in parametre_listesi:
            if param.name in ['kp_derinlik', 'ki_derinlik', 'integral_sinir'] and param.value < 0.0:
                return SetParametersResult(
                    successful=False,
                    reason=f"{param.name} negatif olamaz!"
                )
            if param.name == 'max_izinli_derinlik' and param.value <= 0.0:
                return SetParametersResult(
                    successful=False,
                    reason="max_izinli_derinlik sıfırdan büyük olmalıdır!"
                )
        return SetParametersResult(successful=True)

    def hedef_derinlik_alindi(self, hedef_mesaj: Float32):
        """Görev yöneticisinden gelen hedef derinliği sınırlar dahilinde kaydeder."""
        maks_izinli = float(self.get_parameter('max_izinli_derinlik').value)
        istenen_derinlik = float(hedef_mesaj.data)

        if istenen_derinlik > maks_izinli:
            self.get_logger().warn(f"Hedef derinlik sınır aşıldı! {maks_izinli}m 'ye çekildi.")
            self._hedef_derinlik = maks_izinli
        elif istenen_derinlik < 0.0:
            self.get_logger().warn("Hedef derinlik negatif olamaz, 0.0 m olarak belirlendi.")
            self._hedef_derinlik = 0.0
        else:
            self._hedef_derinlik = istenen_derinlik

    def derinlik_geribesleme_alindi(self, derinlik_mesaj: Float32):
        """Derinlik sensöründen yeni ölçüm geldiğinde kaydeder ve zaman damgasını günceller."""
        self._guncel_derinlik = float(derinlik_mesaj.data)
        self._son_derinlik_zamani = self.get_clock().now()
        self._sensor_kayip_uyarildi = False

    def denetim_dongusu(self):
        """
        10 Hz frekansında çalışan ayrık zamanlı PI denetim algoritması.
        Sensör veri akışı kesilirse emniyet tedbiri olarak komutu sıfırlar.
        """
        anlik_zaman = self.get_clock().now()
        dt = (anlik_zaman - self._son_dongu_zamani).nanoseconds / 1e9
        self._son_dongu_zamani = anlik_zaman

        if dt <= 0.0:
            dt = 0.1

        
        gecen_sure = (anlik_zaman - self._son_derinlik_zamani).nanoseconds / 1e9
        if gecen_sure > 1.0:
            if not self._sensor_kayip_uyarildi:
                self.get_logger().error("SENSÖR KAYIP! Dikey komut = 0")
                self._sensor_kayip_uyarildi = True
            self._integral_toplami = 0.0
            emniyet_komutu = Float32()
            emniyet_komutu.data = 0.0
            self.yayinici_dikey_komut.publish(emniyet_komutu)
            return

        
        hata = self._hedef_derinlik - self._guncel_derinlik

        kp = float(self.get_parameter('kp_derinlik').value)
        ki = float(self.get_parameter('ki_derinlik').value)
        i_limiti = float(self.get_parameter('integral_sinir').value)

        
        self._integral_toplami += hata * dt

        
        self._integral_toplami = max(-i_limiti, min(i_limiti, self._integral_toplami))

        
        u_hesaplanan = (kp * hata) + (ki * self._integral_toplami)

        
        u_doyum = max(-0.5, min(0.5, float(u_hesaplanan)))

        komut_mesaj = Float32()
        komut_mesaj.data = u_doyum
        self.yayinici_dikey_komut.publish(komut_mesaj)


def main(args=None):
    rclpy.init(args=args)
    denetleyici = DerinlikPIDDenetleyici()
    try:
        rclpy.spin(denetleyici)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            denetleyici.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

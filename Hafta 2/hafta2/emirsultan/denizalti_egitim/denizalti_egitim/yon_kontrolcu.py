#!/usr/bin/env python3
"""
Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama
Düğüm: yon_kontrolcu
Yazar: Emir Sultan (K=8)

Açıklama:
Pusula veya IMU'dan gelen anlık baş açısı (/yon_acisi) ile görev yöneticisinden
gelen hedef yönü (/hedef_yon) kıyaslar. Açı sarılması (angle wrapping / modulo 360)
hesabıyla en kısa yoldan (shortest angular path) dönüş sağlayacak /donus_komutu üretir.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from std_msgs.msg import Float32

# denizalti_msgs mevcutsa doğrudan simülatör durumundan yön alma yeteneği ekle
try:
    from denizalti_msgs.msg import DenizaltiDurum
    DURUM_MSG_MEVCUT = True
except ImportError:
    DURUM_MSG_MEVCUT = False


class PusulaYonDenetleyici(Node):
    """
    Yatay düzlemde (Yaw) yönelme sağlayan oransal rota denetleyicisi.
    """

    def __init__(self):
        super().__init__('yon_kontrolcu')

        # Oransal yön kazancı (default 0.02)
        self.declare_parameter('kp_yon', 0.02)

        self._istenen_yon = 0.0
        self._mevcut_yon = 0.0

        # Hedef yönü yakalamak için TRANSIENT_LOCAL QoS profili
        kalici_qos = QoSProfile(
            depth=10,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )

        # Hedef yön aboneliği
        self.abone_hedef_yon = self.create_subscription(
            Float32,
            '/hedef_yon',
            self.hedef_rota_guncellendi,
            kalici_qos
        )

        # Anlık yön aboneliği
        self.abone_yon_acisi = self.create_subscription(
            Float32,
            '/yon_acisi',
            self.pusula_olcumu_alindi,
            10
        )

        # Simülatörden doğrudan durum aboneliği desteği
        if DURUM_MSG_MEVCUT:
            self.abone_durum = self.create_subscription(
                DenizaltiDurum,
                '/denizalti/durum',
                self.durum_telemetrisi_alindi,
                10
            )

        # Yatay iticilere iletilecek dönüş komutu yayıncısı
        self.yayinici_donus_komutu = self.create_publisher(
            Float32,
            '/donus_komutu',
            10
        )

        # 10 Hz periyodik kontrol döngüsü (dt = 0.1 s)
        self.dongu_zamani = self.create_timer(0.1, self.yon_denetim_adimi)

        self.get_logger().info('Pusula Yön Denetleyicisi (Shortest Path) aktif.')

    def durum_telemetrisi_alindi(self, durum_mesaji: 'DenizaltiDurum'):
        """Simülatör durumundan baş açısını günceller."""
        self._mevcut_yon = float(durum_mesaji.yon)

    def hedef_rota_guncellendi(self, hedef_mesaji: Float32):
        """Yeni hedef pusula açısını günceller."""
        self._istenen_yon = float(hedef_mesaji.data)

    def pusula_olcumu_alindi(self, pusula_mesaji: Float32):
        """Pusuladan gelen anlık yön açısını günceller."""
        self._mevcut_yon = float(pusula_mesaji.data)

    def yon_denetim_adimi(self):
        """
        En kısa açı farkını hesaplayarak oransal denetim sinyali üretir.
        Hata [-180, +180] aralığına normalize edilir.
        """
        ham_fark = self._istenen_yon - self._mevcut_yon

        # Soru 3.3: Açı sarılmasını (Angle Wrapping) çözen en kısa yol bağıntısı
        acisal_hata = ((ham_fark + 180.0) % 360.0) - 180.0

        kp = float(self.get_parameter('kp_yon').value)
        u_hesaplanan = kp * acisal_hata

        # İtici gücü sınırlandırması [-0.5, +0.5]
        u_doyum = max(-0.5, min(0.5, float(u_hesaplanan)))

        komut_mesaji = Float32()
        komut_mesaji.data = u_doyum
        self.yayinici_donus_komutu.publish(komut_mesaji)


def main(args=None):
    rclpy.init(args=args)
    denetleyici = PusulaYonDenetleyici()
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

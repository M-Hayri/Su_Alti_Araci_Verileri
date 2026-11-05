#!/usr/bin/env python3


import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


try:
    from denizalti_msgs.msg import DenizaltiDurum
    DURUM_MSG_MEVCUT = True
except ImportError:
    DURUM_MSG_MEVCUT = False


class HidrostatikDerinlikHesaplayici(Node):
    """
    Basınç sensöründen gelen ham veriyi derinliğe dönüştüren düğüm.
    """

    STANDART_ATMOSFERIK_BASINC = 101325.0  # Pa (1 atm deniz seviyesi)
    YER_CEKIMI_IVMESI = 9.81              # m/s^2

    def __init__(self):
        super().__init__('derinlik_hesaplayici')

        
        self.declare_parameter('su_yogunlugu', 1000.0)

        
        self.abone_basinc = self.create_subscription(
            Float32,
            '/basinc',
            self.basinc_olcumu_alindi,
            10
        )

        
        if DURUM_MSG_MEVCUT:
            self.abone_durum = self.create_subscription(
                DenizaltiDurum,
                '/denizalti/durum',
                self.arac_durumu_alindi,
                10
            )

        
        self.yayinici_derinlik = self.create_publisher(
            Float32,
            '/derinlik',
            10
        )

        self.get_logger().info(
            f'Hidrostatik Derinlik Hesaplayıcı aktif. '
            f'Yoğunluk parametresi: {self.get_parameter("su_yogunlugu").value} kg/m³'
        )

    def arac_durumu_alindi(self, durum_mesaji: 'DenizaltiDurum'):
        """Simülatör durum paketinden gelen basıncı işleme aktarır."""
        self._derinlik_hesapla_ve_yayinla(durum_mesaji.basinc)

    def basinc_olcumu_alindi(self, basinc_mesaji: Float32):
        """Ham basınç telemetrisini işleme alır."""
        self._derinlik_hesapla_ve_yayinla(basinc_mesaji.data)

    def _derinlik_hesapla_ve_yayinla(self, okunan_basinc: float):
        """
        P = P_ortam + rho * g * h bağıntısından h (derinlik) türetir.
        Su yüzeyinin üstü fiziksel olarak anlamlı olmadığından h < 0 durumunda 0.0'a kırpılır.
        """
        yogunluk = float(self.get_parameter('su_yogunlugu').value)
        if yogunluk <= 0.0:
            self.get_logger().error('Geçersiz su yoğunluğu! Pozitif bir değer girilmelidir.')
            return

        fark_basinc = okunan_basinc - self.STANDART_ATMOSFERIK_BASINC
        hesaplanan_h = fark_basinc / (yogunluk * self.YER_CEKIMI_IVMESI)

        gecerli_derinlik = max(0.0, float(hesaplanan_h))

        cikis_mesaji = Float32()
        cikis_mesaji.data = gecerli_derinlik
        self.yayinici_derinlik.publish(cikis_mesaji)


def main(args=None):
    rclpy.init(args=args)
    dugum = HidrostatikDerinlikHesaplayici()
    try:
        rclpy.spin(dugum)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            dugum.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

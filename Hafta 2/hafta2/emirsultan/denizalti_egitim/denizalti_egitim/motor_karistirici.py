#!/usr/bin/env python3
"""
Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama
Düğüm: motor_karistirici
Yazar: Emir Sultan (K=8)

Açıklama:
Derinlik ve yön denetleyicilerinden gelen tek eksenli soyut komutları (/dikey_komut ve
/donus_komutu) alarak aracın fiziksel iticilerine paylaştırır (/itici_komutlari ve
/denizalti/motor_komut). Haberleşme kopukluğu durumunda zaman aşımı (watchdog) mekanizması
ile iticileri emniyetli sıfır (0.0) seviyesine çeker.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Float32MultiArray

try:
    from denizalti_msgs.msg import MotorKomut
    MOTOR_KOMUT_MSG_MEVCUT = True
except ImportError:
    MOTOR_KOMUT_MSG_MEVCUT = False


class IticiGucKaristirici(Node):
    """
    Eksenel hareket komutlarını çoklu itici motor yapılandırmasına haritalayan düğüm.
    """

    ZAMAN_ASIMI_ESIGI = 1.0  # saniye (Watchdog zaman aşımı süresi)

    def __init__(self):
        super().__init__('motor_karistirici')

        self._anlik_dikey_talep = 0.0
        self._anlik_donus_talep = 0.0

        su_an = self.get_clock().now()
        self._son_dikey_mesaj_zamani = su_an
        self._son_donus_mesaj_zamani = su_an

        # Watchdog bayrakları (Saniyede 10 kez basılmasını önler, tek sefer basılır)
        self._dikey_kayip_uyarildi = False
        self._donus_kayip_uyarildi = False

        # Dikey denetleyici komut aboneliği
        self.abone_dikey = self.create_subscription(
            Float32,
            '/dikey_komut',
            self.dikey_itki_girisi,
            10
        )

        # Yön denetleyici komut aboneliği
        self.abone_donus = self.create_subscription(
            Float32,
            '/donus_komutu',
            self.donus_torku_girisi,
            10
        )

        # Çok kanallı eyleyici dizi yayıncısı
        self.yayinici_itici_dizi = self.create_publisher(
            Float32MultiArray,
            '/itici_komutlari',
            10
        )

        # Fiziksel simülatör arabirimi için MotorKomut yayıncısı
        if MOTOR_KOMUT_MSG_MEVCUT:
            self.yayinici_sim_motor = self.create_publisher(
                MotorKomut,
                '/denizalti/motor_komut',
                10
            )

        # 10 Hz frekansında periyodik yayın ve watchdog döngüsü (dt = 0.1 s)
        self.yayin_zamanlayicisi = self.create_timer(0.1, self.itici_komutlarini_dagit)

        self.get_logger().info('İtici Güç Karıştırıcı (Motor Mixer) aktif ve izlemede.')

    def dikey_itki_girisi(self, mesaj: Float32):
        """Dikey derinlik ekseni komutunu kaydeder ve zaman damgasını yeniler."""
        self._anlik_dikey_talep = float(mesaj.data)
        self._son_dikey_mesaj_zamani = self.get_clock().now()
        self._dikey_kayip_uyarildi = False

    def donus_torku_girisi(self, mesaj: Float32):
        """Yatay rotasyon ekseni komutunu kaydeder ve zaman damgasını yeniler."""
        self._anlik_donus_talep = float(mesaj.data)
        self._son_donus_mesaj_zamani = self.get_clock().now()
        self._donus_kayip_uyarildi = False

    def itici_komutlarini_dagit(self):
        """
        Giriş sinyallerini zaman aşımına göre denetler (Watchdog) ve
        fiziksel iticilere uygun komut paketini oluşturup yayınlar.
        """
        simdi = self.get_clock().now()

        # Dikey komut zaman aşımı denetimi
        dikey_gecikme = (simdi - self._son_dikey_mesaj_zamani).nanoseconds / 1e9
        if dikey_gecikme > self.ZAMAN_ASIMI_ESIGI:
            if not self._dikey_kayip_uyarildi:
                self.get_logger().error("KOMUT KAYIP: dikey")
                self._dikey_kayip_uyarildi = True
            self._anlik_dikey_talep = 0.0

        # Dönüş komutu zaman aşımı denetimi
        donus_gecikme = (simdi - self._son_donus_mesaj_zamani).nanoseconds / 1e9
        if donus_gecikme > self.ZAMAN_ASIMI_ESIGI:
            if not self._donus_kayip_uyarildi:
                self.get_logger().error("KOMUT KAYIP: donus")
                self._donus_kayip_uyarildi = True
            self._anlik_donus_talep = 0.0

        # Standart çoklu dizi mesajı [Donus1, Donus2, Dikey1, Dikey2]
        dizi_mesaji = Float32MultiArray()
        dizi_mesaji.data = [
            float(self._anlik_donus_talep),
            float(self._anlik_donus_talep),
            float(self._anlik_dikey_talep),
            float(self._anlik_dikey_talep)
        ]
        self.yayinici_itici_dizi.publish(dizi_mesaji)

        # Simülatör doğrudan MotorKomut bekliyorsa eşleşmeyi yap:
        # sag_motor = +donus, sol_motor = -donus
        # dikey_on = dikey, dikey_arka = dikey
        if MOTOR_KOMUT_MSG_MEVCUT:
            motor_mesaj = MotorKomut()
            motor_mesaj.sag_motor = float(self._anlik_donus_talep)
            motor_mesaj.sol_motor = float(-self._anlik_donus_talep)
            motor_mesaj.dikey_on_motor = float(self._anlik_dikey_talep)
            motor_mesaj.dikey_arka_motor = float(self._anlik_dikey_talep)
            self.yayinici_sim_motor.publish(motor_mesaj)


def main(args=None):
    rclpy.init(args=args)
    karistirici = IticiGucKaristirici()
    try:
        rclpy.spin(karistirici)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            karistirici.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

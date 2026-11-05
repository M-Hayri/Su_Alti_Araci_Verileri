#!/usr/bin/env python3
"""
Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama
Düğüm: gorev_yoneticisi
Yazar: Emir Sultan (K=8)

Açıklama:
Otonom denizaltının durum makinesini (Finite State Machine - FSM) yönetir.
Durum sıralaması: BASLA -> DAL -> DON -> BEKLE -> YUZEY -> BITTI.
Ayrıca harici servis çağrıları (/acil_yuzey ve /devam) ile acil durum yönetimini
sağlar. Hedefler TRANSIENT_LOCAL QoS profili ile yayınlanarak ağa geç katılan
kontrolcülerin bilgi kaybı yaşaması engellenir.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Float32, String
from std_srvs.srv import Trigger

try:
    from denizalti_msgs.msg import DenizaltiDurum
    DURUM_MSG_MEVCUT = True
except ImportError:
    DURUM_MSG_MEVCUT = False


class OtonomGorevFSMYoneticisi(Node):
    """
    Sualtı aracının görev aşamalarını ve durum geçiş koşullarını denetleyen merkezi beyin düğümü.
    """

    # FSM Durum İsimleri
    DURUM_BASLA = "BASLA"
    DURUM_DAL = "DAL"
    DURUM_DON = "DON"
    DURUM_BEKLE = "BEKLE"
    DURUM_YUZEY = "YUZEY"
    DURUM_BITTI = "BITTI"
    DURUM_ACIL = "ACIL"

    def __init__(self):
        super().__init__('gorev_yoneticisi')

        # Görev parametreleri (K=8 için dalış: 2.6m, dönüş: 290.0°, max derinlik: 7.0m)
        self.declare_parameter('dalis_derinligi', 2.6)
        self.declare_parameter('donus_yonu', 290.0)
        self.declare_parameter('max_izinli_derinlik', 7.0)

        # Durum değişkenleri
        self._aktif_durum = self.DURUM_BASLA
        self._mevcut_derinlik = 0.0
        self._mevcut_yon = 0.0
        self._baslangic_yonu = None

        simdi = self.get_clock().now()
        self._durum_baslangic_zamani = simdi
        self._kararlilik_baslangic_zamani = None

        # Soru 3.4: Geç katılan düğümler (Late-joining nodes) için TRANSIENT_LOCAL QoS profili
        hedef_qos = QoSProfile(
            depth=10,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )

        # Durum ve hedef yayıncıları
        self.yayinici_hedef_derinlik = self.create_publisher(Float32, '/hedef_derinlik', hedef_qos)
        self.yayinici_hedef_yon = self.create_publisher(Float32, '/hedef_yon', hedef_qos)
        self.yayinici_gorev_durumu = self.create_publisher(String, '/gorev_durumu', 10)

        # Telemetri abonelikleri
        self.abone_derinlik = self.create_subscription(
            Float32, '/derinlik', self.derinlik_guncelle, 10)
        self.abone_yon = self.create_subscription(
            Float32, '/yon_acisi', self.pusula_guncelle, 10)

        if DURUM_MSG_MEVCUT:
            self.abone_durum = self.create_subscription(
                DenizaltiDurum, '/denizalti/durum', self.simulasyon_durumu_alindi, 10)

        # Emniyet servis sunucuları
        self.servis_acil = self.create_service(
            Trigger, '/acil_yuzey', self.acil_yuzey_servisi)
        self.servis_devam = self.create_service(
            Trigger, '/devam', self.goreve_devam_servisi)

        # 2 Hz FSM durum kontrol zamanlayıcısı (dt = 0.5 s)
        self.fsm_zamani = self.create_timer(0.5, self.durum_makinesi_dongusu)

        # Parametre güvenlik doğrulama kancası
        self.add_on_set_parameters_callback(self.parametre_guvenlik_denetimi)

        self.get_logger().info('Otonom Görev Yöneticisi başlatıldı. İlk Durum: BASLA')

    def simulasyon_durumu_alindi(self, durum: 'DenizaltiDurum'):
        """Simülatör telemetrisini işler."""
        self._mevcut_derinlik = float(durum.derinlik)
        self._mevcut_yon = float(durum.yon)
        if self._baslangic_yonu is None:
            self._baslangic_yonu = float(durum.yon)
            self.hedef_referanslari_yayinla()

    def derinlik_guncelle(self, msg: Float32):
        """Sensörden gelen derinliği günceller."""
        self._mevcut_derinlik = float(msg.data)

    def pusula_guncelle(self, msg: Float32):
        """Pusuladan gelen baş açısını günceller."""
        self._mevcut_yon = float(msg.data)
        if self._baslangic_yonu is None:
            self._baslangic_yonu = float(msg.data)
            self.hedef_referanslari_yayinla()

    def parametre_guvenlik_denetimi(self, parametreler):
        """
        Soru 4.5: Parametre sınır kontrolü (Defensive Programming).
        Geçersiz dalış derinliği veya pusula açısı girilirse işlemi reddeder.
        """
        max_derinlik = float(self.get_parameter('max_izinli_derinlik').value)
        for p in parametreler:
            if p.name == 'dalis_derinligi':
                if not (0.0 <= p.value <= max_derinlik):
                    return SetParametersResult(successful=False, reason="Geçersiz dalış derinliği!")
            elif p.name == 'donus_yonu':
                if not (0.0 <= p.value <= 360.0):
                    return SetParametersResult(successful=False, reason="Dönüş yönü 0-360 arası olmalı!")
        return SetParametersResult(successful=True)

    def acil_yuzey_servisi(self, istek, yanit):
        """
        Acil durum çağrısı: FSM'i derhal ACIL moduna alır ve aracı yüzeye yönlendirir.
        """
        self.gorev_durumu_gecisi(self.DURUM_ACIL)
        yanit.success = True
        yanit.message = "Acil durum başlatıldı! Yüzeye çıkılıyor."
        self.get_logger().error("ACİL YÜZEYE ÇIKIŞ: Operatör emri ile yüzeye yönlenildi!")
        return yanit

    def goreve_devam_servisi(self, istek, yanit):
        """
        Acil durum sonlandırma çağrısı: Sadece ACIL durumundayken DAL moduna dönüşe izin verir.
        """
        if self._aktif_durum == self.DURUM_ACIL:
            self.gorev_durumu_gecisi(self.DURUM_DAL)
            yanit.success = True
            yanit.message = "Görev DAL durumundan devam ediyor."
            self.get_logger().info("GÖREVE DEVAM: Acil durum kaldırıldı, dalışa geçiliyor.")
        else:
            yanit.success = False
            yanit.message = "Cihaz ACIL durumunda değil!"
            self.get_logger().warn("Devam çağrısı reddedildi: Sistem ACIL modunda bulunmuyor.")
        return yanit

    def gorev_durumu_gecisi(self, yeni_durum: str):
        """Durum makinesinde aşama değişimini gerçekleştirir ve hedefleri günceller."""
        self._aktif_durum = yeni_durum
        self._durum_baslangic_zamani = self.get_clock().now()
        self._kararlilik_baslangic_zamani = None

        self.get_logger().info(f"YENİ DURUM: {yeni_durum}")

        durum_msg = String()
        durum_msg.data = yeni_durum
        self.yayinici_gorev_durumu.publish(durum_msg)

        self.hedef_referanslari_yayinla()

    def hedef_referanslari_yayinla(self):
        """Aktif duruma uygun hedef derinlik ve yön referanslarını yayınlar."""
        if self._baslangic_yonu is None:
            return

        param_derinlik = float(self.get_parameter('dalis_derinligi').value)
        param_yon = float(self.get_parameter('donus_yonu').value)

        ref_derinlik = 0.0
        ref_yon = self._baslangic_yonu

        if self._aktif_durum == self.DURUM_BASLA:
            ref_derinlik = 0.0
            ref_yon = self._baslangic_yonu
        elif self._aktif_durum == self.DURUM_DAL:
            ref_derinlik = param_derinlik
            ref_yon = self._baslangic_yonu
        elif self._aktif_durum in [self.DURUM_DON, self.DURUM_BEKLE]:
            ref_derinlik = param_derinlik
            ref_yon = param_yon
        elif self._aktif_durum in [self.DURUM_YUZEY, self.DURUM_BITTI]:
            ref_derinlik = 0.0
            ref_yon = param_yon
        elif self._aktif_durum == self.DURUM_ACIL:
            ref_derinlik = 0.0
            ref_yon = self._mevcut_yon

        msg_d = Float32()
        msg_d.data = float(ref_derinlik)
        self.yayinici_hedef_derinlik.publish(msg_d)

        msg_y = Float32()
        msg_y.data = float(ref_yon)
        self.yayinici_hedef_yon.publish(msg_y)

    def durum_makinesi_dongusu(self):
        """FSM durum geçiş kurallarını periyodik olarak değerlendirir."""
        if self._baslangic_yonu is None:
            return

        simdi = self.get_clock().now()
        durumda_gecen_sure = (simdi - self._durum_baslangic_zamani).nanoseconds / 1e9

        hedef_derinlik = float(self.get_parameter('dalis_derinligi').value)
        hedef_yon = float(self.get_parameter('donus_yonu').value)

        if self._aktif_durum == self.DURUM_BASLA:
            # 3 saniye sensör kararlılaşma beklemesi
            if durumda_gecen_sure >= 3.0:
                self.gorev_durumu_gecisi(self.DURUM_DAL)

        elif self._aktif_durum == self.DURUM_DAL:
            # Derinlik tolerans bandı (|hata| < 0.1 m) ve 3 sn kararlılık şartı
            hata_derinlik = abs(self._mevcut_derinlik - hedef_derinlik)
            if hata_derinlik < 0.1:
                if self._kararlilik_baslangic_zamani is None:
                    self._kararlilik_baslangic_zamani = simdi
                elif (simdi - self._kararlilik_baslangic_zamani).nanoseconds / 1e9 >= 3.0:
                    self.gorev_durumu_gecisi(self.DURUM_DON)
            else:
                self._kararlilik_baslangic_zamani = None

        elif self._aktif_durum == self.DURUM_DON:
            # Açısal tolerans bandı (|hata| < 5.0 derece) ve 3 sn kararlılık şartı
            aci_farki = ((hedef_yon - self._mevcut_yon + 180.0) % 360.0) - 180.0
            if abs(aci_farki) < 5.0:
                if self._kararlilik_baslangic_zamani is None:
                    self._kararlilik_baslangic_zamani = simdi
                elif (simdi - self._kararlilik_baslangic_zamani).nanoseconds / 1e9 >= 3.0:
                    self.gorev_durumu_gecisi(self.DURUM_BEKLE)
            else:
                self._kararlilik_baslangic_zamani = None

        elif self._aktif_durum == self.DURUM_BEKLE:
            # 10 saniye sabit derinlik ve yönde bekleme
            if durumda_gecen_sure >= 10.0:
                self.gorev_durumu_gecisi(self.DURUM_YUZEY)

        elif self._aktif_durum == self.DURUM_YUZEY:
            # Yüzeye ulaşma şartı (derinlik < 0.1 m)
            if self._mevcut_derinlik < 0.1:
                self.gorev_durumu_gecisi(self.DURUM_BITTI)


def main(args=None):
    rclpy.init(args=args)
    yonetici = OtonomGorevFSMYoneticisi()
    try:
        rclpy.spin(yonetici)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            yonetici.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

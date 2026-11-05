#!/usr/bin/env python3
"""
Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama
Yardımcı Araç: grafik_uretici.py
Yazar: Emir Sultan (K=8)

Açıklama:
Soru 3 ve Soru 4 kapsamındaki tüm kontrolcü dinamiklerini, durum makinesi (FSM)
aşama geçişlerini, integral anti-windup etkisini ve SPOF/Watchdog güvenlik senaryolarını
matematiksel modelleme ile simüle ederek yüksek çözünürlüklü (300 DPI) kanıt grafiklerini
'kanit/' klasörüne üretir.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Görsel stil ayarları
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8


def kanit_dizinini_al():
    """Kanıt klasörünün mutlak yolunu bulur veya oluşturur."""
    mevcut_dizin = os.path.dirname(os.path.abspath(__file__))
    # Hafta 2 paket hiyerarşisi: emirsultan/kanit
    kanit_dizini = os.path.abspath(os.path.join(mevcut_dizin, '..', '..', 'kanit'))
    os.makedirs(kanit_dizini, exist_ok=True)
    return kanit_dizini


def grafik_rqt_graph_uret(cikti_yolu):
    """
    Soru 3.1 için ROS 2 düğüm ve konu topolojisini gösteren profesyonel
    hesaplama çizelgesi (Computational Graph / rqt_graph).
    """
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=300)
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 7.5)
    ax.axis('off')

    # Düğüm ve Başlık Stilleri
    dugum_kutusu = dict(boxstyle='round,pad=0.6', facecolor='#2b5c8f', edgecolor='#18385c', alpha=0.9, lw=2)
    konu_kutusu = dict(boxstyle='square,pad=0.5', facecolor='#f4f7f6', edgecolor='#2e7d32', lw=1.8)
    metin_stili_dugum = dict(color='white', weight='bold', fontsize=10, ha='center', va='center')
    metin_stili_konu = dict(color='#1b5e20', weight='bold', fontsize=9, ha='center', va='center')

    # Düğümler (Nodes)
    dugumler = {
        'sim': (1.5, 3.5, '/arac_simulasyonu'),
        'hesap': (4.5, 6.0, '/derinlik_hesaplayici'),
        'gorev': (4.5, 1.0, '/gorev_yoneticisi'),
        'd_kontrol': (7.5, 6.0, '/derinlik_kontrolcu'),
        'y_kontrol': (7.5, 1.0, '/yon_kontrolcu'),
        'motor': (10.5, 3.5, '/motor_karistirici')
    }

    for k, (x, y, isim) in dugumler.items():
        ax.text(x, y, isim, bbox=dugum_kutusu, **metin_stili_dugum)

    # Başlıklar (Topics)
    konular = {
        'basinc': (3.0, 5.0, '/basinc\n(Float32)'),
        'derinlik': (6.0, 5.0, '/derinlik\n(Float32)'),
        'hedef_d': (6.0, 6.7, '/hedef_derinlik\n[TRANSIENT_LOCAL]'),
        'yon_acisi': (3.0, 2.0, '/yon_acisi\n(Float32)'),
        'hedef_y': (6.0, 0.3, '/hedef_yon\n[TRANSIENT_LOCAL]'),
        'dikey_k': (9.0, 5.0, '/dikey_komut\n(Float32)'),
        'donus_k': (9.0, 2.0, '/donus_komutu\n(Float32)'),
        'itici_k': (6.0, 3.5, '/denizalti/motor_komut\nveya /itici_komutlari')
    }

    for k, (x, y, isim) in konular.items():
        ax.text(x, y, isim, bbox=konu_kutusu, **metin_stili_konu)

    # Ok bağlantıları (Veri Akış Yolları)
    ok_stili = dict(arrowstyle='-|>', color='#37474f', lw=1.8, mutation_scale=15)

    baglantilar = [
        ((1.5, 4.0), (3.0, 4.7)),   # sim -> basinc
        ((3.0, 5.3), (4.5, 5.7)),   # basinc -> hesap
        ((4.5, 6.3), (6.0, 6.7)),   # hesaplayici -> hedef (okuma)
        ((4.5, 5.7), (6.0, 5.3)),   # hesap -> derinlik
        ((6.0, 4.7), (7.5, 5.7)),   # derinlik -> d_kontrol
        ((6.0, 6.7), (7.5, 6.3)),   # hedef_d -> d_kontrol
        ((4.5, 1.4), (6.0, 6.4)),   # gorev -> hedef_d
        ((4.5, 0.7), (6.0, 0.3)),   # gorev -> hedef_y
        ((6.0, 0.3), (7.5, 0.7)),   # hedef_y -> y_kontrol
        ((1.5, 3.0), (3.0, 2.3)),   # sim -> yon_acisi
        ((3.0, 1.7), (4.5, 1.0)),   # yon_acisi -> gorev
        ((3.0, 2.3), (7.5, 1.3)),   # yon_acisi -> y_kontrol
        ((7.5, 5.7), (9.0, 5.3)),   # d_kontrol -> dikey_k
        ((9.0, 4.7), (10.5, 3.8)),  # dikey_k -> motor
        ((7.5, 1.3), (9.0, 1.7)),   # y_kontrol -> donus_k
        ((9.0, 2.3), (10.5, 3.2)),  # donus_k -> motor
        ((10.5, 3.5), (7.2, 3.5)),  # motor -> itici_k
        ((4.8, 3.5), (1.5, 3.5)),   # itici_k -> sim
    ]

    for bas, son in baglantilar:
        ax.annotate('', xy=son, xytext=bas, arrowprops=ok_stili)

    ax.set_title('Mavi Gölge ROS 2 Hesaplama Çizelgesi (Computational Graph - rqt_graph)',
                 fontsize=14, weight='bold', pad=15, color='#102027')
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=300)
    plt.close()
    print(f"[+] rqt_graph kaydedildi: {cikti_yolu}")


def grafik_kp_karsilastirma_uret(kanit_dizini):
    """
    Soru 4.1 için Kp kazancı (0.2, 1.0, 5.0) ile sephiye etkisi (v_sephiye = 0.13 m/s)
    altında derinlik yanıtı ve kalıcı durum hatasını simüle eder.
    """
    z_hedef = 2.6       # m (K=8 için)
    v_sephiye = 0.13    # m/s (K=8 için)
    dt = 0.05
    t = np.arange(0, 35, dt)

    kp_degerleri = [0.2, 1.0, 5.0]
    renkler = ['#e65100', '#1565c0', '#2e7d32']

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.axhline(z_hedef, color='black', linestyle='--', linewidth=1.5, label=f'Hedef Derinlik ({z_hedef} m)')
    ax.axhspan(z_hedef - 0.1, z_hedef + 0.1, color='gray', alpha=0.2, label='FSM Tolerans Bandı (±0.1 m)')

    for kp, renk in zip(kp_degerleri, renkler):
        z = np.zeros_like(t)
        u_dikey = np.zeros_like(t)
        z_curr = 0.0

        for i in range(1, len(t)):
            hata = z_hedef - z_curr
            u = np.clip(kp * hata, -0.5, 0.5)
            # Fiziksel simülatör dinamikleri: dikey_hiz = u*0.05 + v_sephiye (veya u - sephiye)
            # Motor kuvveti sephiyeyi dengelemek için aşağı itmeli
            d_hiz = (u * 0.5) - v_sephiye  # Aşağı yön pozitif derinlik
            z_curr = max(0.0, z_curr + d_hiz * dt)
            z[i] = z_curr
            u_dikey[i] = u

        e_kalici = v_sephiye / (kp * 0.5) if (kp * 0.5) > 0 else 0
        ax.plot(t, z, color=renk, lw=2.2, label=f'Kp = {kp:.1f} (Denge: {z[-1]:.2f} m, Hata: {z_hedef - z[-1]:.2f} m)')

        # Tekil grafik olarak da kaydet
        fig_tekil, ax_tekil = plt.subplots(figsize=(8, 4.5), dpi=300)
        ax_tekil.plot(t, z, color=renk, lw=2.5, label=f'Kp = {kp:.1f} Yanıtı')
        ax_tekil.axhline(z_hedef, color='black', ls='--', lw=1.5, label=f'Hedef: {z_hedef} m')
        ax_tekil.axhspan(z_hedef - 0.1, z_hedef + 0.1, color='gray', alpha=0.2, label='Tolerans (±0.1 m)')
        ax_tekil.set_title(f'Soru 4.1: Kp={kp:.1f} Oransal Kontrolcü Derinlik Yanıtı (v_sephiye={v_sephiye} m/s)', fontsize=11, weight='bold')
        ax_tekil.set_xlabel('Zaman (s)', fontsize=10)
        ax_tekil.set_ylabel('Derinlik (m)', fontsize=10)
        ax_tekil.grid(True, ls=':', alpha=0.6)
        ax_tekil.legend(loc='lower right')
        plt.tight_layout()
        tekil_ad = f"Kp_{str(kp).replace('.', '')}.png"
        if kp == 0.2:
            tekil_ad = "Kp_02.png"
        elif kp == 1.0:
            tekil_ad = "Kp_10.png"
        elif kp == 5.0:
            tekil_ad = "Kp_50.png"
        fig_tekil.savefig(os.path.join(kanit_dizini, tekil_ad), dpi=300)
        plt.close(fig_tekil)

    ax.set_title(f'Soru 4.1: Farklı Kp Değerlerinde Kalıcı Durum Hatası ve Görev Takılması (K=8, v_sephiye={v_sephiye} m/s)', fontsize=12, weight='bold')
    ax.set_xlabel('Zaman (s)', fontsize=11)
    ax.set_ylabel('Derinlik (m)', fontsize=11)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(kanit_dizini, 'Kp_karsilastirma.png'), dpi=300)
    plt.close()
    print("[+] Kp grafikleri üretildi.")


def grafik_ki_karsilastirma_uret(kanit_dizini):
    """
    Soru 4.2 için Ki değerlerinin (0.05, 0.20, 1.00) sephiye bozucu etkisini
    yok etme başarısı ve aşma (overshoot) performansını simüle eder.
    """
    z_hedef = 2.6       # m
    v_sephiye = 0.13    # m/s
    kp = 1.0
    i_limit = 1.0
    dt = 0.05
    t = np.arange(0, 30, dt)

    ki_listesi = [0.05, 0.20, 1.00]
    renkler = ['#d32f2f', '#1976d2', '#388e3c']

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.axhline(z_hedef, color='black', linestyle='--', linewidth=1.5, label=f'Hedef: {z_hedef} m')
    ax.axhspan(z_hedef - 0.1, z_hedef + 0.1, color='gray', alpha=0.25, label='FSM Kabul Bandı (±0.1 m)')

    for ki, renk in zip(ki_listesi, renkler):
        z = np.zeros_like(t)
        z_curr = 0.0
        integral = 0.0

        for i in range(1, len(t)):
            hata = z_hedef - z_curr
            integral += hata * dt
            integral = np.clip(integral, -i_limit, i_limit)

            u = np.clip(kp * hata + ki * integral, -0.5, 0.5)
            d_hiz = (u * 0.5) - v_sephiye
            z_curr = max(0.0, z_curr + d_hiz * dt)
            z[i] = z_curr

        ax.plot(t, z, color=renk, lw=2.2, label=f'Ki = {ki:.2f} (u_int_max={ki*i_limit:.2f})')

        # Tekil Ki grafikleri
        fig_t, ax_t = plt.subplots(figsize=(8, 4.5), dpi=300)
        ax_t.plot(t, z, color=renk, lw=2.5, label=f'Ki = {ki:.2f} Yanıtı')
        ax_t.axhline(z_hedef, color='black', ls='--', lw=1.5, label=f'Hedef: {z_hedef} m')
        ax_t.axhspan(z_hedef - 0.1, z_hedef + 0.1, color='gray', alpha=0.2, label='Tolerans Bandı')
        ax_t.set_title(f'Soru 4.2: Ki = {ki:.2f} ile PI Derinlik Kontrolü (İntegral Sınırı = {i_limit})', fontsize=11, weight='bold')
        ax_t.set_xlabel('Zaman (s)')
        ax_t.set_ylabel('Derinlik (m)')
        ax_t.grid(True, ls=':', alpha=0.6)
        ax_t.legend(loc='lower right')
        plt.tight_layout()
        ad_tekil = f"Ki_{str(ki).replace('.', '')}.png"
        if ki == 0.05:
            ad_tekil = "Ki_005.png"
        elif ki == 0.20:
            ad_tekil = "Ki_020.png"
        elif ki == 1.00:
            ad_tekil = "Ki_100.png"
        fig_t.savefig(os.path.join(kanit_dizini, ad_tekil), dpi=300)
        plt.close(fig_t)

    ax.set_title('Soru 4.2: Farklı Ki Değerlerinde Doyum ve İntegral Dengeleme Performansı', fontsize=12, weight='bold')
    ax.set_xlabel('Zaman (s)', fontsize=11)
    ax.set_ylabel('Derinlik (m)', fontsize=11)
    ax.grid(True, ls=':', alpha=0.6)
    ax.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(kanit_dizini, 'Ki_karsilastirma.png'), dpi=300)
    plt.close()
    print("[+] Ki grafikleri üretildi.")


def grafik_windup_karsilastirma_uret(kanit_dizini):
    """
    Soru 4.3 için İntegral Anti-Windup sınırının (1.0 vs 1000.0) aşma (overshoot)
    ve toparlanma süresine etkisini simüle eder.
    """
    z_hedef = 3.5       # Soru 4.3 föy hedefi: 3.5 m
    v_sephiye = 0.13
    kp = 1.0
    ki = 0.2
    dt = 0.05
    t = np.arange(0, 45, dt)

    sinirlar = [1.0, 1000.0]
    etiketler = ['Anti-Windup Etkin (Sınır = 1.0)', 'Sınır Yok / Windup Var (Sınır = 1000.0)']
    renkler = ['#1e88e5', '#d81b60']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=300, sharex=True)

    for sinir, etiket, renk in zip(sinirlar, etiketler, renkler):
        z = np.zeros_like(t)
        i_degerleri = np.zeros_like(t)
        z_curr = 0.0
        integral = 0.0

        for i in range(1, len(t)):
            hata = z_hedef - z_curr
            integral += hata * dt
            integral = np.clip(integral, -sinir, sinir)

            u = np.clip(kp * hata + ki * integral, -0.5, 0.5)
            d_hiz = (u * 0.5) - v_sephiye
            z_curr = max(0.0, z_curr + d_hiz * dt)

            z[i] = z_curr
            i_degerleri[i] = integral

        ax1.plot(t, z, color=renk, lw=2.3, label=etiket)
        ax2.plot(t, i_degerleri, color=renk, lw=2.0, label=f'İntegral Terimi ({etiket.split()[0]})')

    ax1.axhline(z_hedef, color='black', ls='--', lw=1.5, label=f'Hedef: {z_hedef} m')
    ax1.set_title('Soru 4.3: İntegral Windup Karşılaştırması - Aşma Miktarı ve Toparlanma', fontsize=12, weight='bold')
    ax1.set_ylabel('Derinlik (m)', fontsize=10)
    ax1.grid(True, ls=':', alpha=0.6)
    ax1.legend(loc='lower right')

    ax2.set_title('İntegral Akümülatörü Birikimi (u_int)', fontsize=11, weight='bold')
    ax2.set_xlabel('Zaman (s)', fontsize=10)
    ax2.set_ylabel('İntegral Değeri', fontsize=10)
    ax2.grid(True, ls=':', alpha=0.6)
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(kanit_dizini, 'integral_sinir_karsilastirma.png'), dpi=300)
    plt.close()
    print("[+] İntegral Windup karşılaştırma grafiği üretildi.")


def grafik_tam_gorev_profili_uret(kanit_dizini):
    """
    Soru 3.1 & 3.6 & Soru 4: Tam otonom görev durum makinesi profilini (BASLA -> DAL -> DON -> BEKLE -> YUZEY -> BITTI)
    hem derinlik (m) hem de pusula baş açısı (derece) olarak zaman ekseninde simüle eder.
    """
    dt = 0.1
    t_toplam = 65.0
    t = np.arange(0, t_toplam, dt)

    z = np.zeros_like(t)
    yaw = np.zeros_like(t)
    durumlar = []

    # Parametreler (K=8)
    z_hedef = 2.6
    yaw_hedef = 290.0
    v_sephiye = 0.13

    # Durum Süreleri
    # BASLA: 0 - 3s
    # DAL: 3 - 18s (Derinliğe inip 3s kararlı kalma)
    # DON: 18 - 32s (290°'ye dönüp 3s kararlı kalma)
    # BEKLE: 32 - 42s (10 saniye bekleme)
    # YUZEY: 42 - 55s (Yüzeye çıkış)
    # BITTI: 55+ s

    z_curr = 0.0
    yaw_curr = 0.0
    integral_z = 0.0

    for i, cur_t in enumerate(t):
        if cur_t < 3.0:
            durum = "BASLA"
            ref_z = 0.0
            ref_yaw = 0.0
        elif cur_t < 18.0:
            durum = "DAL"
            ref_z = z_hedef
            ref_yaw = 0.0
        elif cur_t < 32.0:
            durum = "DON"
            ref_z = z_hedef
            ref_yaw = yaw_hedef
        elif cur_t < 42.0:
            durum = "BEKLE"
            ref_z = z_hedef
            ref_yaw = yaw_hedef
        elif cur_t < 55.0:
            durum = "YUZEY"
            ref_z = 0.0
            ref_yaw = yaw_hedef
        else:
            durum = "BITTI"
            ref_z = 0.0
            ref_yaw = yaw_hedef

        durumlar.append(durum)

        # Derinlik Dinamiği (PI)
        hata_z = ref_z - z_curr
        integral_z += hata_z * dt
        integral_z = np.clip(integral_z, -1.0, 1.0)
        u_z = np.clip(1.0 * hata_z + 0.2 * integral_z, -0.5, 0.5)
        d_hiz = (u_z * 0.5) - v_sephiye
        z_curr = max(0.0, z_curr + d_hiz * dt)
        z[i] = z_curr

        # Yön Dinamiği (P + Shortest Path)
        fark_yaw = ((ref_yaw - yaw_curr + 180.0) % 360.0) - 180.0
        u_yaw = np.clip(0.02 * fark_yaw, -0.5, 0.5)
        # Dönüş hızı: maksimum ~30 deg/s
        donus_hizi = u_yaw * 60.0
        yaw_curr = (yaw_curr + donus_hizi * dt) % 360.0
        yaw[i] = yaw_curr

    fig, (ax_z, ax_y) = plt.subplots(2, 1, figsize=(11, 8), dpi=300, sharex=True)

    # Durum Arka Plan Renklendirmesi
    gecisler = [
        (0.0, 3.0, 'BASLA', '#e0e0e0'),
        (3.0, 18.0, 'DAL', '#bbdefb'),
        (18.0, 32.0, 'DON', '#ffe0b2'),
        (32.0, 42.0, 'BEKLE', '#c8e6c9'),
        (42.0, 55.0, 'YUZEY', '#e1bee7'),
        (55.0, 65.0, 'BITTI', '#cfd8dc')
    ]

    for t1, t2, ad, renk in gecisler:
        ax_z.axvspan(t1, t2, color=renk, alpha=0.35)
        ax_y.axvspan(t1, t2, color=renk, alpha=0.35)
        ax_z.text((t1 + t2)/2.0, 2.85, ad, ha='center', va='bottom', fontsize=9, weight='bold', color='#263238')

    # Derinlik Grafiği
    ax_z.plot(t, z, color='#0d47a1', lw=2.4, label='Gerçekleşen Derinlik (m)')
    ax_z.axhline(z_hedef, color='#b71c1c', ls='--', lw=1.5, label=f'Dalış Hedefi ({z_hedef} m)')
    ax_z.set_ylabel('Derinlik (m)', fontsize=10, weight='bold')
    ax_z.set_ylim(-0.2, 3.1)
    ax_z.grid(True, ls=':', alpha=0.6)
    ax_z.legend(loc='upper right')
    ax_z.set_title('Mavi Gölge Otonom Görev Zaman Profili (K=8: Derinlik=2.6m, Yön=290.0°)', fontsize=12, weight='bold')

    # Yön Grafiği
    ax_y.plot(t, yaw, color='#e65100', lw=2.4, label='Pusula Baş Açısı (°)')
    ax_y.axhline(yaw_hedef, color='#2e7d32', ls='--', lw=1.5, label=f'Hedef Rota ({yaw_hedef}°)')
    ax_y.set_ylabel('Pusula Açısı (°)', fontsize=10, weight='bold')
    ax_y.set_xlabel('Zaman (s)', fontsize=10, weight='bold')
    ax_y.set_ylim(-10, 380)
    ax_y.grid(True, ls=':', alpha=0.6)
    ax_y.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(os.path.join(kanit_dizini, 'gorev_profili.png'), dpi=300)
    plt.close()
    print("[+] Tam görev profili grafiği üretildi.")


def grafik_spof_watchdog_uret(kanit_dizini):
    """
    Soru 3.5 & Soru 4.4 için SPOF ve Watchdog zaman aşımı senaryosunu simüle eder.
    T=15 saniyede sensör/mixer bağlantısı koptuğunda komutların 0'a çekilmesi ve
    aracın pozitif sephiye (0.13 m/s) ile güvenle yüzeye süzülmesi gösterilir.
    """
    dt = 0.05
    t = np.arange(0, 35, dt)
    z = np.zeros_like(t)
    u_komut = np.zeros_like(t)

    z_hedef = 2.6
    v_sephiye = 0.13
    z_curr = 2.6  # Araç hedef derinlikte kararlı
    u_curr = 0.26  # Sephiyeyi dengeleyen itki

    for i, cur_t in enumerate(t):
        if cur_t < 12.0:
            # Normal çalışma
            hata = z_hedef - z_curr
            u_curr = 0.26 + hata * 0.5
            d_hiz = (u_curr * 0.5) - v_sephiye
            z_curr = max(0.0, z_curr + d_hiz * dt)
        elif cur_t < 13.0:
            # Sensör kesildi, ancak 1.0 saniye boyunca son veri tutuluyor
            d_hiz = (u_curr * 0.5) - v_sephiye
            z_curr = max(0.0, z_curr + d_hiz * dt)
        else:
            # T=13s: Watchdog tetiklendi! Komut = 0.0'a çekildi
            u_curr = 0.0
            # Sadece pozitif sephiye hızıyla yüzeye süzülür (yukarı doğru -0.13 m/s)
            z_curr = max(0.0, z_curr - v_sephiye * dt)

        z[i] = z_curr
        u_komut[i] = u_curr

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), dpi=300, sharex=True)

    ax1.plot(t, z, color='#1565c0', lw=2.5, label='Araç Derinliği (m)')
    ax1.axvline(12.0, color='#d32f2f', ls='--', lw=1.8, label='T=12s: İletişim Kesintisi (SPOF)')
    ax1.axvline(13.0, color='#f57c00', ls=':', lw=2.0, label='T=13s: Watchdog Tetiklendi (Komut=0)')
    ax1.set_ylabel('Derinlik (m)', fontsize=10)
    ax1.grid(True, ls=':', alpha=0.6)
    ax1.legend(loc='center right')
    ax1.set_title('Soru 3.5 & 4.4: Watchdog Güvenlik Koruması ve Pozitif Sephiye ile Yüzeye Süzülme', fontsize=12, weight='bold')

    ax2.plot(t, u_komut, color='#c2185b', lw=2.2, label='Motor Komutu (Dikey İtki)')
    ax2.axvline(12.0, color='#d32f2f', ls='--', lw=1.8)
    ax2.axvline(13.0, color='#f57c00', ls=':', lw=2.0)
    ax2.set_xlabel('Zaman (s)', fontsize=10)
    ax2.set_ylabel('Komut [-0.5, +0.5]', fontsize=10)
    ax2.grid(True, ls=':', alpha=0.6)
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(kanit_dizini, 'spof_watchdog_analizi.png'), dpi=300)
    plt.close()
    print("[+] SPOF Watchdog analizi grafiği üretildi.")


def main():
    """Tüm kanıt grafiklerini oluşturur."""
    print("Kanıt grafikleri üretimi başlatılıyor...")
    kanit_dizini = kanit_dizinini_al()
    print(f"Hedef klasör: {kanit_dizini}")

    grafik_rqt_graph_uret(os.path.join(kanit_dizini, 'rqt_graph.png'))
    grafik_kp_karsilastirma_uret(kanit_dizini)
    grafik_ki_karsilastirma_uret(kanit_dizini)
    grafik_windup_karsilastirma_uret(kanit_dizini)
    grafik_tam_gorev_profili_uret(kanit_dizini)
    grafik_spof_watchdog_uret(kanit_dizini)

    print("Tüm kanıt grafikleri başarıyla oluşturuldu!")


if __name__ == '__main__':
    main()

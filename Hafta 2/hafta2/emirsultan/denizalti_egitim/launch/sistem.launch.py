#!/usr/bin/env python3
"""
Mavi Gölge Otonom Denizaltı Sistemi Başlatma Dosyası
Öğrenci: Emir Sultan (K=8)
Bu dosya sistemdeki tüm düğümleri tek bir yapılandırma dosyası (sistem_params.yaml)
üzerinden ayağa kaldırır.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Yapılandırma YAML dosyasının paket paylaşım yolunu belirle
    paket_paylasim_dizini = get_package_share_directory('denizalti_egitim')
    parametre_dosyasi = os.path.join(
        paket_paylasim_dizini,
        'config',
        'sistem_params.yaml'
    )

    # 1. Araç Simülasyonu Düğümü (Fiziksel model)
    simulasyon_dugumu = Node(
        package='denizalti_egitim',
        executable='arac_simulasyonu',
        name='arac_simulasyonu',
        parameters=[parametre_dosyasi],
        output='screen'
    )

    # 2. Basınçtan Derinlik Hesaplayıcı Düğüm
    derinlik_hesaplayici_dugumu = Node(
        package='denizalti_egitim',
        executable='derinlik_hesaplayici',
        name='derinlik_hesaplayici',
        parameters=[parametre_dosyasi],
        output='screen'
    )

    # 3. Dikey Derinlik PI Kontrolcü Düğümü
    derinlik_kontrolcu_dugumu = Node(
        package='denizalti_egitim',
        executable='derinlik_kontrolcu',
        name='derinlik_kontrolcu',
        parameters=[parametre_dosyasi],
        output='screen'
    )

    # 4. Yön (Heading/Yaw) Kontrolcü Düğümü
    yon_kontrolcu_dugumu = Node(
        package='denizalti_egitim',
        executable='yon_kontrolcu',
        name='yon_kontrolcu',
        parameters=[parametre_dosyasi],
        output='screen'
    )

    # 5. İtici Kuvvet Karıştırıcı (Motor Mixer) Düğümü
    motor_karistirici_dugumu = Node(
        package='denizalti_egitim',
        executable='motor_karistirici',
        name='motor_karistirici',
        parameters=[parametre_dosyasi],
        output='screen'
    )

    # 6. Otonom Görev Durum Yöneticisi Düğümü (FSM)
    gorev_yoneticisi_dugumu = Node(
        package='denizalti_egitim',
        executable='gorev_yoneticisi',
        name='gorev_yoneticisi',
        parameters=[parametre_dosyasi],
        output='screen'
    )

    return LaunchDescription([
        simulasyon_dugumu,
        derinlik_hesaplayici_dugumu,
        derinlik_kontrolcu_dugumu,
        yon_kontrolcu_dugumu,
        motor_karistirici_dugumu,
        gorev_yoneticisi_dugumu
    ])

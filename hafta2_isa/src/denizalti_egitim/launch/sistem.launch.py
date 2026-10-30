import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('denizalti_egitim'),
        'config',
        'sistem_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='denizalti_egitim',
            executable='arac_simulasyonu.py',
            name='arac_simulasyonu',
            parameters=[config]
        ),
        Node(
            package='denizalti_egitim',
            executable='derinlik_hesaplayici',
            name='derinlik_hesaplayici',
            parameters=[config]
        ),
        Node(
            package='denizalti_egitim',
            executable='derinlik_kontrolcu',
            name='derinlik_kontrolcu',
            parameters=[config]
        ),
        Node(
            package='denizalti_egitim',
            executable='yon_kontrolcu',
            name='yon_kontrolcu',
            parameters=[config]
        ),
        Node(
            package='denizalti_egitim',
            executable='motor_karistirici',
            name='motor_karistirici',
            parameters=[config]
        ),
        Node(
            package='denizalti_egitim',
            executable='gorev_yoneticisi',
            name='gorev_yoneticisi',
            parameters=[config]
        ),
    ])

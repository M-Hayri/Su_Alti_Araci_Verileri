
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='denizalti_egitim',
            executable='derinlik_sensoru',
            name='derinlik_sensoru',
            output='screen'
        ),
        Node(
            package='denizalti_egitim',
            executable='derinlik_kontrolcu',
            name='derinlik_kontrolcu',
            output='screen'
        ),
        Node(
            package='denizalti_egitim',
            executable='derinlik_gostergesi',
            name='derinlik_gostergesi',
            output='screen'
        ),
    ])

import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'denizalti_egitim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='isa',
    maintainer_email='isa@todo.todo',
    description='Mavi Golge ROS 2 Egitim Paketi',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'arac_simulasyonu.py = denizalti_egitim.arac_simulasyonu:main',
            'derinlik_hesaplayici = denizalti_egitim.derinlik_hesaplayici:main',
            'derinlik_kontrolcu = denizalti_egitim.derinlik_kontrolcu:main',
            'yon_kontrolcu = denizalti_egitim.yon_kontrolcu:main',
            'motor_karistirici = denizalti_egitim.motor_karistirici:main',
            'gorev_yoneticisi = denizalti_egitim.gorev_yoneticisi:main',
        ],
    },
)
from setuptools import find_packages, setup
import os
from glob import glob



package_name = 'denizalti_egitim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
        os.path.join('share', package_name, 'launch'),
        glob(os.path.join('launch', '*.launch.py'))
        ),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='timur',
    maintainer_email='timur@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'derinlik_sensoru = denizalti_egitim.derinlik_sensoru:main',
            'derinlik_gostergesi = denizalti_egitim.derinlik_gostergesi:main',
            'derinlik_kontrolcu = denizalti_egitim.derinlik_kontrolcu:main',
    
        ],
    },
)

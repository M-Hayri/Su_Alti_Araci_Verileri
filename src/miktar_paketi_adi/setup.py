from setuptools import find_packages, setup

package_name = 'miktar_paketi_adi'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mesamorta',
    maintainer_email='mesamorta@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'su_alti_durum = miktar_paketi_adi.su_alti_durum:main',
		'su_alti_dinleyici = miktar_paketi_adi.su_alti_dinleyici:main',
        ],
    },
)

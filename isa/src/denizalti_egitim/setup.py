from setuptools import find_packages, setup

package_name = 'denizalti_egitim'

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
    maintainer='isa',
    maintainer_email='isa@todo.todo',
    description='Denizalti Python Dugumleri',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'derinlik_sensoru = denizalti_egitim.derinlik_sensoru:main',
            'derinlik_gostergesi = denizalti_egitim.derinlik_gostergesi:main',
            'derinlik_kontrolcu = denizalti_egitim.derinlik_kontrolcu:main',
        ],
    },
)
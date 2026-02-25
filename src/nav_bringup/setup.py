from setuptools import setup
import os
from glob import glob

package_name = 'nav_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*.*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Piyush',
    maintainer_email='you@example.com',
    description='Nav2 + SLAM bringup for indoor delivery robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)

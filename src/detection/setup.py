from setuptools import find_packages, setup

package_name = 'detection'

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
    maintainer='wasiq',
    maintainer_email='03337406603s@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tensorflow_detection=detection.tensorflow_detection:main',
            'yolov8=detection.yolov8:main'
        ],
    },
)

from setuptools import find_packages, setup

setup(
    name='earthos',
    packages=find_packages(),
    version='0.1.0',
    description='Ecosophy EarthOS API bindings',
    author='Ecosophy',
    license='BSD',
    install_requires=[
        'requests',
        'Pillow',
        'numpy',
    ],
    tests_require=[
        'pytest',
    ],
)

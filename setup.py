from setuptools import setup, find_packages

setup(
    name='qns',
    author='elliot',
    version='0.0.3',
    description='A discrete time scheduler designed for Quantum Network',
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={'docs': ['.gitkeep']},
    install_requires=[
    ],
)

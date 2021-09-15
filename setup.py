from setuptools import setup, find_packages

setup(
    name='qns',
    author='elliot',
    version='0.1.0',
    description='A discrete time scheduler designed for Quantum Network',
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={'docs': ['.gitkeep']},
    setup_requires=["numpy"],
    install_requires=["numpy"],
)
from setuptools import setup, find_packages

setup(
    name = 'qns',
    author = 'elliot',
    version = '0.1',
    description='A quantum network simulator',
    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {'docs':['.gitkeep']},
    install_requires = [
    ],
)
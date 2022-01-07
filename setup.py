from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='qns',
    author='elliot',
    version='0.1.1',
    description='A discrete-event scheduler designed for quantum networks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/ertuil/SimQN",
    exclude_package_data={'docs': ['.gitkeep']},
    setup_requires=["numpy"],
    install_requires=["numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

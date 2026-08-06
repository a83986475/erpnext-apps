from setuptools import setup, find_packages

setup(
    name="solua_home",
    version="0.0.1",
    description="ERPNext 中文定制功能",
    author="Solua Home, Lda",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
)
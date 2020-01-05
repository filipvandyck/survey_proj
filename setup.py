# requires libbz2-dev

from setuptools import setup, find_packages

setup(
    name='validate',
    version='0.0.1',
    packages=find_packages(include=['validate', 'validate.*']),
    install_requires=[
        'pandas',
        'numpy',
        'geopandas',
        'folium',
        'rtree'
	]
)

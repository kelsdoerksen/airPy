"""
Setup structure following:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="airpy",
    version="1.1.0",
    description="A Google Earth Engine extraction tool for air quality studies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kelsdoerksen/airPy",
    author="Kelsey Doerksen",
    author_email="kelsey.doerksen@cs.ox.ac.uk",
    keywords="air quality, google earth engine, machine learning",
    package_dir={'': 'airpy'},
    packages=find_packages(where="airPy"),
    python_requires=">=3.6, <4",
    entry_points={
        "console_scripts": [
            "run_airpy=airpy.run_airpy:main",
        ],
    },
)

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
    name="pyaq",
    version="1.0.0",
    description="A Google Earth Engine extraction tool for air quality studies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kelsdoerksen/py-aq",
    author="Kelsey Doerksen",
    author_email="kelsey.doerksen@cs.ox.ac.uk",
    keywords="air quality, google earth engine, machine learning",
    package_dir={'': 'src'},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    entry_points={
        "console_scripts": [
            "generate-config=pyaq.generate_config:main",
            "run-pyaq=pyaq.gee_processing_tool_pyaq:main",
        ],
    },
)
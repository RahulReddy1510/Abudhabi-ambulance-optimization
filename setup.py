from setuptools import setup, find_packages

setup(
    name="abudhabi-ambulance-optimization",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pulp>=2.7.0",
        "geopandas>=0.14.2",
        "shapely>=2.0.3",
        "numpy>=1.26.3",
        "pandas>=2.1.4",
        "scipy>=1.12.0",
        "matplotlib>=3.8.2",
        "seaborn>=0.13.2",
        "libpysal>=4.9.2",
        "esda>=2.6.0",
        "pyyaml>=6.0.1",
    ],
    author="Rahul Reddy Koulury",
    description="Emergency Ambulance Coverage Optimization for Abu Dhabi",
    python_requires=">=3.10",
)

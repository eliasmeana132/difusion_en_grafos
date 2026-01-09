from setuptools import setup, find_packages

setup(
    name="pelado",
    version="1.0.0",
    author="Your Name",
    description="Libreria para difusion en grafos y metodo de pelado.",
    packages=find_packages(),
    install_requires=[
        "networkx",
        "matplotlib",
        "pandas",
        "numpy",
        "plotly",
    ],
    python_requires=">=3.7",
)
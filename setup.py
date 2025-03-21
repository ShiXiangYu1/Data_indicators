from setuptools import setup, find_packages

setup(
    name="data_insight",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "flask",
        "flask-cors",
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "statsmodels",
        "networkx",
    ],
    python_requires=">=3.8",
) 
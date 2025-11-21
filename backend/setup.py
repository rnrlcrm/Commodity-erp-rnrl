"""Setup file for Cotton ERP Backend."""
from setuptools import setup, find_packages

setup(
    name="cotton-erp-backend",
    version="0.1.0",
    description="Cotton ERP Backend API",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.11",
    install_requires=[
        # Dependencies are managed in requirements.txt
    ],
)

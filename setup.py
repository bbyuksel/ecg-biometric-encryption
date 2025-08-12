"""
Setup script for ECG Signal Biometric Encryption System.

This package provides a comprehensive system for ECG signal biometric encryption
using chaotic systems and machine learning optimization.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ecg-biometric-encryption",
    version="1.0.0",
    author="Beyazit Bestami YUKSEL",
    author_email="yukselbe18@itu.edu.tr",
    description="A novel ECG signal biometric encryption system using chaotic dynamics and ML optimization",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/bbyuksel/ecg-biometric-encryption",
    project_urls={
        "Bug Reports": "https://github.com/bbyuksel/ecg-biometric-encryption/issues",
        "Source": "https://github.com/bbyuksel/ecg-biometric-encryption",
        "Documentation": "https://github.com/bbyuksel/ecg-biometric-encryption/docs",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
        "full": [
            "tensorflow>=2.8.0",
            "scikit-learn>=1.0.0",
            "scipy>=1.7.0",
            "seaborn>=0.11.0",
            "pillow>=8.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ecg-encryption=ecg_gui_all:main",
            "ecg-security-test=brute_force_attack_comparison:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.json", "*.txt", "*.md"],
    },
    keywords=[
        "ecg",
        "biometric",
        "encryption",
        "chaotic",
        "machine-learning",
        "security",
        "biomedical",
        "signal-processing",
        "cryptography",
        "healthcare",
    ],
    platforms=["Windows", "Linux", "macOS"],
    license="MIT",
    zip_safe=False,
    test_suite="tests",
    tests_require=["pytest>=6.2.0"],
)

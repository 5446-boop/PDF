from setuptools import setup, find_packages

setup(
    name="pdf_highlighter",
    version="2.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt5>=5.15.0",
        "PyMuPDF>=1.22.3",
        "pytest>=7.0.0",
        "pytest-qt>=4.2.0",
        "pytest-cov>=4.1.0",
    ],
    author="5446-boop",
    author_email="5446-boop@github.com",
    description="A modern PyQt5-based PDF viewer and highlighter application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/5446-boop/PDF",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pdf_highlighter=src.main:main",
        ],
    },
)
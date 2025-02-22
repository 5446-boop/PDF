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
    description="A modern PyQt5-based PDF viewer and highlighter application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pdf-highlighter=src.main:main",
        ],
    },
)
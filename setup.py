from setuptools import setup, find_packages

setup(
    name="pdf-highlighter",
    version="2.0.0",
    author="5446-boop",
    description="A PyQt5-based PDF viewer and highlighter application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt5>=5.15.0",
        "PyMuPDF>=1.19.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pdf-highlighter=pdf_highlighter.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
    ],
)
from setuptools import setup, find_packages

setup(
    name="pdf_highlighter",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyMuPDF>=1.22.3",
        "pygame>=2.5.2",
    ],
    author="5446-boop",
    description="A PDF highlighting application with GUI interface",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pdf_highlighter=pdf_highlighter.app:main",
        ],
    },
)
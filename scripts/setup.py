from setuptools import setup, find_packages

setup(
    name="open-code-ide",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyQt6"
    ],
    entry_points={
        "console_scripts": [
            "open-code-ide = main:main"
        ]
    },
)

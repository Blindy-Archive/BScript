import pathlib

from setuptools import setup, find_packages

from BScript import __version__

VERSION = __version__
DESCRIPTION = 'BScript'
# LONG_DESCRIPTION = 'A package inspired by django model system and implemented that system for mssql via using pyodbc'
HERE = pathlib.Path(__file__).parent

# The text of the README file
README =""

# Setting up
setup(
    name="BScript",
    version=VERSION,
    author="Mehmet Berkay Özbay",
    author_email="<berkayozbay64@gmail.com>",
    url="https://github.com/bilinenkisi/msorm",
    description=DESCRIPTION,

    packages=find_packages(),
    install_requires=["requests",
                      "pyjsparser",
                      "colorama"
                      ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'BScript'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

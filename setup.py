import re

from typing import List

import setuptools

requirements: List[str] = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = ""
author = ""
with open("yarpc/__init__.py") as f:
    cont = f.read()
    version_gr = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', cont, re.MULTILINE
    )
    if version_gr:
        version = version_gr.group(1)
    author_gr = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', cont, re.MULTILINE)
    if author_gr:
        author = author_gr.group(1)

setuptools.setup(
    name="yarpc",
    version=version,
    author=author,
    description="RPC system used in IOMirea messenger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IOMirea/yarpc",
    install_requires=requirements,
    python_requires=">=3.7.1",
    packages=setuptools.find_packages(),
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
)

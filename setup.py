import re

import setuptools  # type: ignore

install_requires = ["aioredis"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = ""
author = ""

with open("jarpc/__init__.py") as f:
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
    name="jarpc",
    version=version,
    author=author,
    author_email="fogaprod@gmail.com",
    description="RPC over redis communication library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IOMirea/jarpc",
    install_requires=install_requires,
    python_requires=">=3.6",
    packages=setuptools.find_packages(),
    package_data={"jarpc": ["py.typed"]},
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Topic :: Software Development :: Object Brokering",
        "Typing :: Typed",
    ],
)

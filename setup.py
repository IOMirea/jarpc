import os
import re

import setuptools  # type: ignore

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


init_py = os.path.join(os.path.dirname(__file__), "jarpc", "__init__.py")

with open(init_py) as f:
    cont = f.read()

    str_regex = r"['\"]([^'\"]*)['\"]"
    try:
        version = re.findall(rf"^__version__ = {str_regex}$", cont, re.MULTILINE)[0]
    except IndexError:
        raise RuntimeError(f"Unable to find version in {init_py}")

    try:
        author = re.findall(rf"^__author__ = {str_regex}$", cont, re.MULTILINE)[0]
    except IndexError:
        raise RuntimeError(f"Unable to find author in {init_py}")

install_requires = ["aioredis", "ply"]

classifiers = [
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
]

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
    classifiers=classifiers,
)

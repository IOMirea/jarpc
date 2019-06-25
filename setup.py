import setuptools

from typing import List


requirements: List[str] = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iomirea_rpc",
    version="0.1.0",
    author="Eugene Ershov",
    description="RPC system used in IOMirea messenger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IOMirea/rpc",
    install_requires=requirements,
    python_requires=">=3.5.3",
    packages=setuptools.find_packages(),
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

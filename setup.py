"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject

Based on https://github.com/pypa/sampleproject
Licensed under the MIT License.
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="bbcradio",
    version="0.1.0",
    description="Unofficial API for BBC radio station schedules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StevenMaude/bbc-radio-schedules",
    author="Steven Maude",
    # author_email='author@example.com',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="bbc, radio, schedule",
    packages=find_packages(),
    python_requires=">=3.6, <4",
    install_requires=["lxml~=4.6.2", "requests~=2.25.1"],
    extras_require={"dev": ["black==20.8b1"],},
    entry_points={"console_scripts": ["bbcradio_cli=bbcradio.cli:main",],},
)

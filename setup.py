"""Setup module for the DeON package."""

from setuptools import setup, find_packages

setup(name='deon',
    version='0.0.1',
    description='Definition or not?',
    url='https://github.com/dkmfbk/deon',
    author='Giulio Petrucci (petrux)',
    author_email='giulio.petrucci@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    dependency_links=[],
    zip_safe=False)

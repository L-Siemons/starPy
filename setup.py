from distutils.core import setup
from setuptools import setup, find_packages

descrip='''
 
This a small module for handling star files.
 
'''
 
setup(
    name='starPy',
    version='0.0.1',
    author='L. Siemons',
    author_email='lucas.siemons@googlemail.com',
    packages=find_packages(),
    license='LICENSE.txt',
    description=descrip,
    long_description=open('readme.md').read(),
    install_requires=['pandas','numpy',],

)

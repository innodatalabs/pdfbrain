import sys
from setuptools import setup, find_packages
from pdfbrain import __version__

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requires = [x.strip() for x in f if x.strip()]

setup(
    name        = 'pdfbrain',
    version     = __version__,
    description = 'Parsing PDF files with pdfium',
    author      ='Mike Kroutikov',
    author_email='mkroutikov@innodata.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url         ='https://github.com/innodatalabs/pdfbrain',
    license     ='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=install_requires,
)

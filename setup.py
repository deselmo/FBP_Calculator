from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

name = 'fbp_calculator'

github = 'https://github.com/deselmo/FBP_Calculator'

with open(path.join(here, name, 'release.py')) as f:
    # Defines __version__
    exec(f.read())

setup(
    name=name,
    version=__version__, # pylint: disable=E0602
    description='FBP Calculator is a Python tool to calculate predicor for Reaction System.',
    url=github,
    author='William Guglielmo',
    author_email='william@deselmo.com',
    packages=find_packages(),
    install_requires=[
        'pyeda>=0.28.0',
        'PyQt5>=5.10.1',
        'XlsxWriter>=1.0.2'
    ],
    entry_points={
        'console_scripts': [
            '{}={}:main'.format(name, name),
        ],
    },
    project_urls={
        'Bug Reports': '{}/issues'.format(github),
        'Source': '{}/'.format(github),
    },
    license='MIT'
)
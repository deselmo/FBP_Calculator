from setuptools import setup, find_packages
from codecs import open
from os import path

dir_setup = path.dirname(path.realpath(__file__))

with open(path.join(dir_setup, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name='fbp_calculator',
        version='0.0.1',
        description='Program to calculate of formula based predictor of the reaction system.',
        url='https://github.com/deselmo/Tirocinio',
        author='deselmo',
        author_email='william@deselmo.com',

        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
        ],

        python_requires='>=3.5',
        py_modules=["six"],
        install_requires=['sympy>=1.1.1', 'PyQt5>=5.10.1'],

        project_urls={
            'Bug Reports': 'https://github.com/deselmo/Tirocinio/issues',
            'Source': 'https://github.com/deselmo/Tirocinio',
        },
    )

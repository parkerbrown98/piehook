from setuptools import setup, find_packages

setup(
    name='piehook',
    version='0.2.2',
    description='A simple hook system for Python.',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'piehook = piehook.cli:main'
        ]
    },
    python_requires='>=3.6',
)
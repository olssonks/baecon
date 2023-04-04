from setuptools import setup, find_packages
import os
VERSION = '0.1' 
DESCRIPTION = 'Baecon: Basic Experiment Control'

# Fetches description from README.rst file
with open(os.path.join(os.getcwd(), 'README.rst'), "r") as f:
    LONG_DESCRIPTION = f.read()

# Setting up
setup(
        name="baecon", 
        version=VERSION,
        author="Kevin S. Olsson",
        author_email="",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        zip_safe=False,
        keywords=['python', 'experiment', 'laboratory', 
                  'control', 'instrument'],
        classifiers= [          
            "Intended Audience :: Science/Research",
            "License :: Public Domain",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.8",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Documentation :: Sphinx",
            "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator", ## Maybe??
            "Topic :: System :: Hardware",
            "Development Status :: 2 - Pre-Alpha"
        ]
)
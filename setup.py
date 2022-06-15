from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = 'Python package for handling HDF5 data structurally compatible with Signal Plant.'
LONG_DESCRIPTION = ''

# Setting up
setup(       
        name="planter", 
        version=VERSION,
        author="Richard Redina, Jakub Hejc",
        author_email="<hejc.ja@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            'h5py>=3.6.0',
            'numpy>=1.21.2',
        ],        
        keywords=['python', 'signal plant', 'hdf5', 'h5py'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",            
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
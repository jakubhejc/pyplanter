from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Python package for handling HDF5 data structurally compatible with Signal Plant.'
LONG_DESCRIPTION = ''

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="planter", 
        version=VERSION,
        author="Richard Redina, Jakub Hejc",
        author_email="<hejc.ja@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'signal plant', 'hdf5', 'h5py'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",            
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
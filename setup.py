VERSION='0.2'

kwargs = {
    'packages' : ['testoob'],
    'package_dir' : {'': 'src'},

    # meta-data
    'name'             : 'testoob',
    'version'          : VERSION,
    'author'           : 'Ori Peleg',
    'author_email'     : 'testoob@gmail.com',
    'url'              : 'http://testoob.sourceforge.net',
    'download_url'     : 'http://sourceforge.net/project/showfiles.php?group_id=138557',
    'license'          : 'LGPL',
    'platforms'        : ['any'],
    'description'      : 'TestOOB - An advanced unit testing framework',
}


kwargs['long_description'] = """
TestOOB - Testing Out Of (The) Box

TestOOB is a bundle of extensions to Python's built-in unit
testing framework (module unittest).

It provides advanced features, like easy and extensible filtering
and reporting options.

It can be used as a drop-in replacement for unittest: simply
replace unittest.main() with testoob.main()!

Even more options are available if you use testoob in your tests.
See the homepage for details!
""".strip()

kwargs['classifiers'] = """
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Programming Language :: Python
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
""".strip().splitlines()

# ============================================================================

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
import sys
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# run setup
from distutils.core import setup

setup(**kwargs)

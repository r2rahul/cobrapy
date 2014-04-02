Installation of pyGLPK in Python
================================

Please note that pyGLPK is not the same as python-glpk.

GNU/Linux Installation of pyGLPK in Python
------------------------------------------

1. Install the glpk and gmp library packages. You will need the
   development versions if they are available. You will also need
   development headers for Python itself. For example, Ubuntu and Debian
   Wheezy (7.0) users would type the following into the command line:
   ``sudo apt-get install libglpk-dev libgmp-dev python-dev python-setuptools``
   Debian Squeeze (6.0) users will need to build libgmp from source.

2. install pyglpk with easy\_install using the following command in the
   terminal: ``sudo easy_install glpk``

MAC OS X Installation of pyGLPK in Python
-----------------------------------------

1. Install homebrew if you don't have it. This may require downloading
   Xcode from the AppStore and Command Line Tools for XCode from
   https://developer.apple.com/devcenter/mac/index.action. If you're
   already using macports then just use that to install glpk.
   ``brew install glpk``

2. install pyglpk with easy\_install using the following command in the
   terminal: ``sudo easy_install glpk``

Windows Installation of pyGLPK in Python
----------------------------------------

Download and install the executable from
`here <https://sourceforge.net/projects/opencobra/files/python/cobra/extras/pyGLPK/>`_.

#!/bin/bash
cd $HOME # home should be in /home/travis

if [ "$JYTHON" = "true" ]; then
    sudo apt-get install libglpk-java
    wget http://clostridium.ucsd.edu/jython-installer-2.7-b1.jar
    wget http://clostridium.ucsd.edu/jsbml-0.8-with-dependencies.jar
    java -jar jython-installer-2.7-b1.jar -s -d $HOME/jython
fi

if [ "$JYTHON" = "false" ]; then
    sudo apt-get install libglpk-dev python-scipy libgmp-dev
    pip install glpk
    ln -s /usr/lib/python2.7/dist-packages/scipy ~/virtualenv/python2.7/lib/python2.7/site-packages/
    wget http://clostridium.ucsd.edu/libsbml-5.6.0_built_with_py.tar.gz
    tar xzf libsbml-5.6.0_built_with_py.tar.gz
    cd libsbml-5.6.0/
    sudo make install
fi

cd $TRAVIS_BUILD_DIR

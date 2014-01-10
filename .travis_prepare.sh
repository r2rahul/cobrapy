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
    cd /home/travis
    wget http://clostridium.ucsd.edu/libSBML-5.9.0_compiled.tar.gz
    tar xzf libSBML-5.9.0_compiled.tar.gz
    cd libSBML-5.9.0-Source
    sudo make install
    cd $TRAVIS_BUILD_DIR

    ln -s /usr/lib/python2.7/dist-packages/scipy ~/virtualenv/python2.7/lib/python2.7/site-packages/
    pip install glpk 
fi

cd $TRAVIS_BUILD_DIR

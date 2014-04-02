# Installation
For installation help, please use the
[Google Group](http://groups.google.com/group/cobra-pie).

## Installation of COBRApy in Python
All releases require Python 2.7 to be installed before proceeding. 
Mac OS X (10.7+) and Ubuntu ship with Python. Windows users without python 
can download and install python from the [python 
website](http://www.python.org/download/releases/2.7.6/).


### Windows
For Windows, download and install the appropriate 32 bit or 64 bit installer,
both of which can be downloaded from the [python package
index](https://pypi.python.org/pypi/cobra/).

### Mac OS X
[Install pip](http://pip.readthedocs.org/en/latest/installing.html), and then
run the following command in a terminal

    pip install --use-wheel cobra

### Linux
[Install pip](http://pip.readthedocs.org/en/latest/installing.html). Afterwards
install the build dependencies for the solver. You will need development
libraries for libglpk and python itself, as well as Cython. On Ubuntu/Debian,
this can be done with

    sudo apt-get install python-dev libglpk-dev
    sudo pip install cython

Now, COBRApy can be installed with

    sudo pip install cobra


### "Hacking" version
First, clone the git repository using your preferred mothod. Cloning from your
own [github fork](https://help.github.com/articles/fork-a-repo) is recommended!
Afterwards, open a terminal, enter the cobrapy repository and run the following command:

    python setup.py develop --user

If the command fails with an error about the --user option not being recognized,
it means setuptools is not installed. Either install setuptools before
trying again, or instead run ```sudo python setup.py develop```

## Installation of alternate linear programming solvers
COBRApy comes with bindings to the GLPK solver (called "cglpk"). Three other
bindings to linear programming solvers are implemented:

 * GLPK through [pyGLPK](http://tfinley.net/software/pyglpk/) ("glpk")
 * Gurobi ("gurobi")
 * ILOG/CPLEX ("cplex")

ILOG/CPLEX and Gurobi are commercial software packages that, currently, 
provide free licenses for academics and support both linear and quadratic 
programming. GLPK is an opensource linear programming solver; however, it 
does not support quadratic programming and is not as robust as the 
commercial solvers when it comes to mixed-integer linear programming.

These bindings can be installed by following these instructions:

 * pyGLPK :doc:[installation](documentation_builder/pyglpk_install.rst)
 * [ILOG/CPLEX Academic](https://www.ibm.com/developerworks/university/academicinitiative/)
 * [ILOG/CPLEX Commercial](http://www.ibm.com/software/integration/optimization/cplex-optimizer/)
 * [Gurobi Academic & Commercial](http://gurobi.com)

## Installation of Optional Dependencies
Installation instructions are not provided for these libraries. However, 
many of them can be easily built on GNU/Linux with easy_install. On windows, 
many can downloaded from [this site](http://www.lfd.uci.edu/~gohlke/pythonlibs/).

1. [libsbml](http://sbml.org) >= 4.0 to read/write SBML files
  * Can be installed with ```pip install python-lisbsbml-experimental```
  * [Windows installer](http://www.lfd.uci.edu/~gohlke/pythonlibs/#libsbml)
2. [numpy](http://numpy.org) >= 1.6.1 and [scipy](http://scipy.org) >= 0.11 for
   ArrayBasedModel, double_deletion analysis, and saving to MAT formats.
  * Windows installers for 
  [numpy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) and 
  [scipy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)
3. [Parallel Python](http://parallelpython.org) for parallel processing.
4. [MATLAB](http://mathworks.com) and 
   [mlabwrap](http://mlabwrap.sourceforge.net) for connecting to the COBRA 
   Toolbox for MATLAB.
  * Installation is tricky on most platforms.


## Testing your installation
1. Start python
2. Type the following into the Python shell

```python
from cobra.test import test_all
test_all()
```


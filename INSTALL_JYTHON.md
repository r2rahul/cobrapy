Installation instructions for Jython are detailed below. The 
Python instructions will be approrpriate for most users. For installation 
help, please use the [Google Group](http://groups.google.com/group/cobra-pie).

For usage instructions, please see the 
[documentation](https://cobrapy.readthedocs.org/en/latest/)

--------------------------------------------------------------------------------

#INSTALLATION - Jython
All releases require Jython (2.5+).  JSBML (http://sbml.org) is required for reading / writing SBML files.
NOTE: ArrayBasedModel, double_deletion analysis, saving to MAT formats, parallel processing,  and connecting to the
COBRA Toolbox for MATLAB are currently unavailable when using Jython.

I. Releases - Hosted on http://opencobra.sourceforge.net
   A. Download the most recent bzipped archive.
   B. Unzip the archive and make sure that the toplevel directory is in your Java CLASSPATH.
   C. Install a linear programming solver (Section III).

II. Development Code - Hosted on github
  NOTE: Not intended for general users.  Some functions require advanced capabilities / settings.  Unless you're
  willing to deal with headaches and heartaches it's better to install one of the releases.
  1. git pull https://github.com/opencobra/cobrapy.git
  2. Add the cobrapy directory to your Java CLASSPATH.
  3. Install a linear programming solver (Section III).

III. Installation of linear programming solvers
    On Jython, cobrapy currently supports two linear programming solvers: ILOG/CPLEX and Gurobi.

    A. ILOG/CPLEX and Gurobi are commercial software packages that, currently, provide free licenses for academics and
    support both linear and quadratic programming.
        1. Please download the software from their respective sites, install according to their instructions, and make
        sure that their Java jars are in your Java CLASSPATH.
        2. Current links are listed below. If they don't work then search using google.
          * [ILOG/CPLEX Academic](https://www.ibm.com/developerworks/university/academicinitiative/)
          * [ILOG/CPLEX Commercial](http://www.ibm.com/software/integration/optimization/cplex-optimizer/)
          * [Gurobi Academic & Commercial](http://gurobi.com)

    B. GLPK:  We are exploring the possibility of using GLPK through [GLPK for Java](http://glpk-java.sourceforge.net);
    however, we've encountered irregular memory errors that we'll need to trace before listing it as a supported solver.
    Advanced users may try http://glpk-java.sourceforge.net at their own risk.

IV. Test your installation.
  A. Start Jython
  B. Enter: from cobra.test import test_all
  C. Enter: test_all()

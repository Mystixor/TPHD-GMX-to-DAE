# TPHD-GMX-to-DAE
This Python 3 (!!!) tool exports basic model data from TPHD's GMX files and puts them into Collada (.dae) files.
It works with some but not all models and does not work perfectly with any model yet.

The Collada code is taken unedited from Pycollada's repository:
https://github.com/pycollada/pycollada


Instructions:

"python -m pip install numpy" (Only on the first time, if you did not have Numpy installed yet)

"python buildDAE.py your-gmx-file.gmx"

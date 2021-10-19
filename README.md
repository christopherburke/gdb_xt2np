# gdb_xt2np
GDB python tool to pretty print, examine, and debug c++ [Xtensor](https://xtensor.readthedocs.io/en/latest/) containers. Xtensor is a c++ library for scientific computing using multidimensional arrays while providing a very python numpy-esque interface. Using the python GDB interface, this tool converts an xtensor to a numpy array and saves it to the GDB python interactive session allowing one to examine the xtensor array using matplotlib, printing numpy slices, etc..

Here is a screenshot of the gdb_xt2np helper in action. During a debugging session using eclipse IDE, in c++, I use xtensor to create a 2-d (100x200) array filled with uniformly random distributed integers. At a gdb breakpoint, I loaded the gdb_xt2np.py helper script.

Execute the gdb convenience function enabled by gdb_xt2np.py to examine the contents of the variable 'ar2' from the source code.
`(gdb) p $xt2np("ar2")`

The xt2np function loads the xtensor container into a numpy array, then uses the native python numpy pretty printing to show a summary of the array contents, and then returns showing properties of the xtensor varible. In addition, to printing the 'ar2' variable summary, the variable is now available in the python interactive session within gdb. I use matplotlib.imshow to display the contents of the 'ar2' variable.

![Eclipse debugging session with the gdb_xt2np helper](gdb_xt2np_example.png)

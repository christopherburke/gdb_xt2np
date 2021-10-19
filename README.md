# gdb_xt2np
GDB python tool to pretty print, examine, and debug c++ [Xtensor](https://xtensor.readthedocs.io/en/latest/) containers. Xtensor is a c++ library for scientific computing using multidimensional arrays while providing a very python numpy-esque interface. Using the python GDB interface, this tool converts an xtensor to a numpy array and saves it to the GDB python interactive session allowing one to examine the xtensor array using matplotlib, printing numpy slices, etc..

Here is a screenshot of the gdb_xt2np helper in action. During a debugging session using eclipse IDE, in c++, I use xtensor to create a 2-d (100x200) array filled with uniformly random distributed integers. At a gdb breakpoint, I loaded the gdb_xt2np.py helper script.

Execute the gdb convenience function enabled by gdb_xt2np.py to examine the contents of the variable 'ar2' from the source code.
`(gdb) p $xt2np("ar2")`

The xt2np function loads the xtensor container into a numpy array, then uses the native python numpy pretty printing to show a summary of the array contents, and then returns showing properties of the xtensor varible. In addition, to printing the 'ar2' variable summary, the variable is now available in the python interactive session within gdb. I use matplotlib.imshow to display the contents of the 'ar2' variable.

![Eclipse debugging session with the gdb_xt2np helper](gdb_xt2np_example.png)

### Version 0.1

### FAQ
* For modest sized arrays gdb complains about a max-size-value limit. Within gdb, `set max-size-value unlimited` will remove this warning, but beware you are not trying to bring too large of an array to numpy. Your system needs memory for holding multiple copies

### AUTHORS
Christopher J. Burke. Inspiration for this came from several blogs and posts.
* [Greg Law pyton pretty printer basics](https://undo.io/resources/gdb-watchpoint/here-quick-way-pretty-print-structures-gdb/)
* [Mark Williamson continuing pretty printer for structures](https://undo.io/resources/gdb-watchpoint/debugging-pretty-printers-gdb-part2/)
* [Darlan Cavalcante Moreira python pretty printer helper for armadillo linear algebra library](https://github.com/darcamo/gdb_armadillo_helpers)
* [Tyler Hoffman blog about making python packages available to gdb's python](https://interrupt.memfault.com/blog/using-pypi-packages-with-gdb#using-python-pypi-packages-within-gdb-lldb)
* [M. Mo for the ideas of making gdb variables into numpy arrays enabling interactive python access](https://www.codeproject.com/Articles/669606/Analyzing-C-Cplusplus-matrix-in-the-gdb-debugger-w)
* [Python API documentation](https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html#Python-API)
* Lots of stackoverflow posts

### Dependencies & Setup
Well I'm not going to sugar coat it. It's a pain and I am not thrilled over all these hoops I needed to get the dependencies to work. The main problem is that I use a CentOS 7 linux machine that I don't have root access. I also am using gdb with eclipse IDE. I point out specific steps for my setup, and you will need to tailor them for your system, debugging IDE, etc..

CentOS 7 comes with ancient gcc 4.8.5 compiler. For c++17 standards (for xtensor) and more recent gdb one needs at least gcc 8+. It seems that in order to upgrade gcc without breaking things on CentOS, one needs to use 'Software Collection' devtoolset. Read about it [here](https://ahelpme.com/linux/centos7/how-to-install-new-gcc-and-development-tools-under-centos-7/) and the particular one they installed devtoolset-8 [here](https://ahelpme.com/linux/centos7/how-to-install-gnu-gcc-8-on-centos-7/). At a terminal, one invokes `scl enable devtoolset-8 bash` in order to enable the gcc 8+ tool chain. However, even starting eclipse IDE from a bash shell with devtoolset-8 enabled, the eclipse IDE was still using the gcc 4 compiler and old gdb. The only way I found to have eclipse adopt the gcc 8+ tool chain is to set a command alias in my .bashrc

`alias eclipse='scl enable devtoolset-8 /eta-earth/cjburke/local/eclipse/eclipse`

Starting eclipse IDE in this manner got the gcc 8+ tool chain available from within eclipse. Within IDE gdb session `(gdb) show version` reports 8.2 in my setup. Also within gdb you can show what python version is being used
```
(gdb) py
>import sys
>print(sys.version)
>end
2.7.5 (default, Nov 16 2020, 22:23:17) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
```
NOTE: The version of python in gdb has nothing to do with any python you may have on your system. If you don't compile gdb yourself, but use gdb from a package manager, then gdb uses a python library version. In other words, the python used by gdb is self contained within gdb itself and the python version used was decided when gdb was compiled by the package managers. One can look in the gdb binary for the python symbols `ldd $(which gdb) | grep python` yields `libpython2.7.so.1.0 => /lib64/libpython2.7.so.1.0 (0x00007f8026f60000)` on my setup. Unfortunately, the version compiled in as part of the devtoolset-8 is a python 2 version. The question arises then how do I install numpy, matplotlib, and any other python package for use in the gdb version of python? The normal solution is install packages in the python path that the gdb python uses. One can use
```
(gdb) py
>import sys
>print(sys.path)
>end
```
to show the path where the gdb python version expects to find site-packages. Unfortunately, I don't have write permission to the location it was using as part of the devtools-8 install. My workaround was to use my preferred anaconda python manager and its enviroment support. I created a python 2.7 environment called py27 `conda create -n py27 python=2.7`. Then activate the py27 environment and I installed numpy and matplotlib which grabs the appropriate python 2.7 versions of these packages. `conda activate py27` `conda install numpy` `conda install matplotlib`. Unfortunately, it was not enough to call eclipse IDE after activating the py27 environment. I needed to resort to setting shell environment variable $PYTHONPATH in the eclipse alias. I set the $GDBPYDIR to the head directory of the py27 files setup by the conda environment.
```
export GDBPYDIR=/eta-earth/cjburke/local/.conda/envs/py27
alias eclipse='export PYTHONPATH=${PYTHONPATH}:${GDBPYDIR}/lib/python2.7/site-packages; export LD_LIBRARY_PATH=${GDBPYDIR}/lib:${LD_LIBRARY_PATH}; scl enable devtoolset-8 /eta-earth/cjburke/local/eclipse/eclipse'
```
It was also necessary to add the python lib directory to LD_LIBRARY_PATH because there was a collision for a library that matplotlib needs in the system and the one that it needs from the environment.

Whew.. kinda sucky. I also haven't figured out why my ~/.gdbinit file is not working to automatically source the gdb_xt2np.py file at startup, so I have manually source it within eclipse IDE gdb version.

###TODOs
* Add support for memory ordering (i.e., column or row ordering). xt2np doesn't check the ordering of the xtensor container or set ordering when creating the numpy array
* xt2np sets a python global variable with the same name as the variable. There is probably a safer way to do this and have the variable be available in the gdb python interpreter.

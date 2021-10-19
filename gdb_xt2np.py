import gdb.types
from re import search as resrch
import numpy as np

# pyXt2Np is a subclass of gdb.Function class
class pyXt2Np (gdb.Function):
    """
    GDB convenience function that prints the dimensions and shape of an xtensor container using python. It also makes a numpy copy of the xtensor container as a global variable with the same variable name in the gdb interactive space, so that you can examine the data using python 
    Usage: (gdb) p $xt2np("arr")
	where arr is an xt::xarray or xtensor or xtensor_fixed
	You must give the variable name as a string (e.g., surrounded in quotes)
    """
    def __init__ (self):
	# Call the __init__ of the parent class gdb.Function
    	# Which registers the convenience function name
    	super (pyXt2Np, self).__init__ ("xt2np")

    def invoke (self, var_name):
    	# Implementation of the xt2np convenience function within gdb
	# The first argument needs to be a string containing the variable
	#  name rather than the variable itself because
	#  we need the variable name later on to do method calls, save it as python global variable...
	# Name comes in with literal quotes so strip them away
	var_name_str = str(var_name).strip('"')
	# Get the actual gdb.Value for this variable
	var = gdb.parse_and_eval(var_name_str)

	# Determine if the variable passed is a valid xtensor type
	# Get the type of variable
	var_type = gdb.types.get_basic_type(var.type).name
	#print var_type
	# Look for xt::.*_container
	want_type = "xt::.*_container"
	if resrch(want_type, var_type):
	    # There was an xtensor container sent
	    # Confirm that the m_shape and m_storage fields are present
	    if gdb.types.has_field(var.type, 'm_shape') and gdb.types.has_field(var.type, 'm_storage'):
		# xtensor_fixed needs different treatment than xarray and xtensor to get shape and length
		want_type = "xt::xfixed_container"
		if not resrch(want_type, var_type):
		    # Handle cases of xarray and xtensor
                    # Get dimension from method call
		    dim = int(gdb.parse_and_eval('{}.dimension()'.format(var_name_str)))
		    shape_list = []
		    data_len = 1
		    for i in range(dim):
		    	curdim = int(gdb.parse_and_eval('{0}.shape()[{1:d}]'.format(var_name_str,i)).referenced_value())
		    	shape_list.append(curdim)
		    	data_len = data_len * curdim
		    # Get all the data from a gdb 'artifical array'
		    arr_data = gdb.parse_and_eval('*({0}.m_storage.p_begin)@{1:d}'.format(var_name_str, data_len))

		else:
		    # Handle case of xtensor_fixed
		    # The dimension shapes are constants and given in string representation of template
		    #  gdb.type.template_argument() can return those template arguments
                    shape_str = str(var.type.template_argument(1))
                    try:
		        found = resrch('<(.+?)>', shape_str).group(1)
		    except:
			return "Could not determine shape and size of a xtensor_fixed object"
		    shape_list = [int(x) for x in found.split(',')]
		    dim = len(shape_list)
		    data_len = 1
		    for i in range(dim):
			data_len = data_len * shape_list[i]
		    # Data is already in std::array
		    arr_data = gdb.parse_and_eval('{0}.m_storage._M_elems'.format(var_name_str))
		# python dictionary of accepted types go from C -> numpy dtypes
		nptypes = {'double':'d', 'float':'f', 'unsigned long':'L', 'unsigned int':'I', 'unsigned short':'H', 'long':'l','int':'i','short':'h'}
		gdb_type = arr_data[0].type.name
		if not gdb_type in nptypes:
			return "Could not find {} type equivalent to numpy".format(gdb_type)
		npUseType = nptypes[gdb_type]
		# make the numpy variable storage space
		np_arr_data = np.zeros((data_len,), dtype=npUseType)
		# iterate through the data array to load it into numpy array
		for i in range(data_len):
			np_arr_data[i] = arr_data[i]
		# Now reshape
		np_arr_fin = np_arr_data.reshape(shape_list)
		# Now make available global under same name as under gdb
		# According to google making global variable using exec and
	        #  making global variables in general is bad practice,
	        #  but here it is nonetheless
		com_str = "globals()['{}'] = np.copy(np_arr_fin)".format(var_name_str)
		exec(com_str)
		# Use numpy's builin pretty printing to show the contents of xtensor
		exec("print({})".format(var_name_str))
		# Return the make stats about xtensor
	        return "xtensor {0} Dimen: {1:d} Shape: {2} Len: {3:d} GDBType: {4} NPType: {5}-{6}".format(var_name_str,dim, str(shape_list), data_len, gdb_type, npUseType, np_arr_fin.dtype)
	else:
	    # There was not an xtensor container as argument return
	    return "The argument to $xt2np is not an xtensor container"

# Need to instantiate the class
pyXt2Np()

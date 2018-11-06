# BasicTools module
#
# Andriy Zhugayevych (azh@ukr.net), Sergey Matveev(matseralex@yandex.ru)
# zhugayevych.me/python/BasicTools/index.htm
# created 9.08.2014, modified 1.11.2018


import numpy
import os
import struct

class BasicTools:
	def __init__(self):
		""

	def ReadBIN(self, filename, nodescription=False, code=[0,0,0,0], dimensions=[0], datapos=0, printout=False ):

		if printout:
		    print("ReadBIN is working...")
		shift = 32
		f = open(filename, 'rb')#open for binary reading
		_order = 'C'
		if (datapos != 0):
		    f.read(datapos)
		
		if code == [0,0,0,0]:
		    format_id = struct.unpack('=i', f.read(4))[0]
		else:
		    format_id = 1760568055
		if printout:
		    print("format id = ", format_id)
	################################################################################################################
		if code == [0,0,0,0]:
		    elements_type = struct.unpack('=b', f.read(1))[0]
		else:
		    elements_type = code[0]
		if printout:
		    print("elements type = ", elements_type)
	################################################################################################################
		if code == [0,0,0,0]:
		    elements_size = struct.unpack('=b', f.read(1))[0]
		else:
		    elements_size = code[1]
		if printout:
		    print("elements size =", elements_size)
	################################################################################################################
		if code == [0,0,0,0]:
		    shape = struct.unpack('=b', f.read(1))[0]
		else:
		    shape = code[2]
		if printout:
		    print("shape =", shape)
	################################################################################################################
		if code == [0,0,0,0]:
		    byte_ordering = struct.unpack('=b', f.read(1))[0]
		else:
		    byte_ordering = code[3]
		if printout:
		    print("bo = ", byte_ordering)
	################################################################################################################
		shift -= 8
		data_to_read = 1
	#   check the shapes of our arrays and set dimensionality
	################################################################################################################
		if (shape in [1,11,12]):#vector
		    if printout:
		        print('vector')
		    if (code == [0,0,0,0]) and (dimensions == [0]):
		        dims = [struct.unpack('=i',f.read(4))[0]]
		    shift -= 4

		elif (shape in [2,21,22]):#matrix
		    if printout:
		        print('matrix')
		    if (shape in [2,21]):
		        if printout:
		            print('C ordered')
		    else:
		        _order = 'F'
		    if printout:
		        print('F ordered')
		    if (code == [0,0,0,0]) and (dimensions == [0]):
		        dims = [struct.unpack('i',f.read(4))[0],struct.unpack('i',f.read(4))[0]]
		    shift -= 8
		    #dims[0] gives number of columns , dims[1] gives number of rows
		elif (shape in [3,31,32]):#symmetric matrix
		    if printout:
		        print('symmetric matrix')
		    if (shape in [3,31]):
		        if printout:
		            print('C ordered')
		    else:
		        _order = 'F'
		        if printout:
		            print('F ordered')
		    if code == [0,0,0,0] and (dimensions == [0]):
		        _dim = struct.unpack('i',f.read(4))[0]
		        dims = [_dim, _dim]
		    shift -= 4
		elif (shape in [41,42,43,44]):#multidimensional array
		    dimensionality = shape - 40
		    if (code == [0,0,0,0]) and ( dimensions == [0]):
		        dims=[]
		        for i in range(dimensionality):
		            dims.append( struct.unpack('i',f.read(4))[0])
		            shift -= 4
		else:
		    print('error: incorrect shapes')
		    f.close()
		    return 1
		if not ( (code == [0,0,0,0]) and (dimensions ==[0])):
		    dims = dimensions
		
		if printout:
		    print(dims)
		format_string = "";
	#   check the byte ordering
	################################################################################################################
		if (byte_ordering == 1):
		    bo = 'native'
		    #print(bo)
		    format_string+='='
		elif (byte_ordering == 2):
		    bo = 'network'
		    format_string+='!'
		    #print(bo)
		elif (byte_ordering == 3):
		    bo = 'big'
		    #print(bo)
		    format_string+='>'
		elif (byte_ordering == 4):
		    bo = 'little'
		    #print(bo)
		    format_string=='<'
		else:
		    print('error : incorrect byte ordering')
		    return 1
		#check elements type and set string with type of data for the numpy array
		if printout:
		    print(bo)
		
		dtype_string=''
	################################################################################################################
		if (elements_type == 1):
		    print('integers',elements_size)
		    format_string +='int'
		    if (elements_size == 1):
		        format_string +='b'
		        dtype_string += '8'
		    elif (elements_size == 2):
		        format_string +='h'
		        dtype_string +='16'
		    elif (elements_size == 4):
		        format_string +='i'
		        dtype_string += '32'
		    elif (elements_size == 8):
		        format_string +='q'
		        dtype_string += '64'
		else:
		    if printout:
		        print('float')
		    dtype_string+= 'float'
		    if (elements_size == 4):
		        format_string += 'f'
		        dtype_string += '32'
		    else:
		        format_string += 'd'
		        dtype_string += '64'
		
		if printout:
		    print('format is ', format_string)
		if (not (elements_size in [1,2,4,8])):
		    print('error: deprecated element size')
		    return 1
	################################################################################################################    
	#Read DATA
		if printout:
		    print(dims)
		
		for i in dims:
		    data_to_read *= i
		#print("shift = ", shift)
		if not nodescription and not(code == [0,0,0,0]):
		    shift = 32
		    f.read(shift)
		elif nodescription and not (code == [0,0,0,0]):
		    shift = 0
		else:
		    f.read(shift)

		a=numpy.zeros(data_to_read, dtype=dtype_string)

		if not (shape in [3,31,32]):
		    for i in range(data_to_read):
		        a[i]  = struct.unpack(format_string, f.read(elements_size))[0]
		    a=a.reshape(dims, order = _order)
		else:
		    #print("shape", shape)
		    a=numpy.zeros(data_to_read, dtype = dtype_string)
		    a=a.reshape(dims, order = _order)
		    for i in range(dims[0]):
		        for j in range(dims[0]):
		            a[i,j]=0.0
		            if shape in [3,31]:
		                if (j<=i):
		                    a[i,j] = struct.unpack(format_string, f.read(elements_size))[0]
		            else:
		                if (j>=i):
		                    a[i,j] = struct.unpack(format_string, f.read(elements_size))[0]
		    
		    a = a + a.transpose(1,0)
		    for i in range(dims[0]):
		        a[i,i]/=2
		    f.close()
		return a


	################################################################################################################    
	################################################################################################################    
	def WriteBIN(self, filename, data_array, order_of_data='C', byte_ordering='native', printout=False):
		if printout:
		    print("\n\nWriteBIN is working...")
		f=open(filename, 'wb')
		dims = data_array.shape
		if (len(dims)>2) and (order_of_data!='C'):
		    print("WARNING: multidimensional case! only C-order. changed the option")
		    order_of_data='C'
		if_symmetric_matrix = False
		written_material = 0
		if (len(dims) == 2) and (dims[0] == dims[1]):
		    if (data_array == data_array.T).all():
		        if_symmetric_matrix = True
		_descriptor_length = 32
	################################################################################################################    
		if (byte_ordering == 'native'):
		    bo = 1
		    #print(bo)
		    format_string='='
		elif (byte_ordering == 'network'):
		    bo = 2
		    format_string='!'
		    print(bo)
		elif (byte_ordering == 'big'):
		    bo = 3
		    #print(bo)
		    format_string='>'
		elif (byte_ordering == 'little'):
		    bo = 4
		    #print(bo)
		    format_string='<'
		else:
		    print('error : incorrect byte ordering')
		    return 1
		if printout:
		    print("format ", byte_ordering)
	#################################################################################################################
		#create destriptor
		#write the format id
		f.write(struct.pack(format_string + 'i', 1760568055 )) # i should put here the real value of the format code
		_descriptor_length -= 4
	#################################################################################################################
		#check elements type
		el_type = ''
		data_type = data_array.dtype
		if ( data_type in [numpy.float32, numpy.float64]):
		    elements_type = 2
		    if data_type == numpy.float32:
		        el_type = 'f'
		    elif data_type == numpy.float64:
		        el_type = 'd'
		elif (data_type in [numpy.int8, numpy.int16, numpy.int32, numpy.int64]):
		    elements_type = 1
		else:
		    print('error : incorrect type of data')
		    return 1
		f.write(struct.pack(format_string+'b', elements_type ))
		if printout:
		    print("type_of_data = ", data_type)
	#    print("elements type = ", elements_type)
		_descriptor_length -= 1
	#################################################################################################################
		#check elements size
		if data_type in [numpy.int64, numpy.float64]:
		    elements_size = 8
		    if data_type == numpy.int64:
		        el_type = 'q'
		elif data_type in [numpy.int32, numpy.float32]:
		    elements_size = 4
		    if data_type == numpy.int32:
		        el_type ='i'
		elif data_type == numpy.int16:
		    elements_size = 2
		    el_type = 'h'
		elif data_type == numpy.int8:
		    elements_size = 1
		    el_type = 'b'
		else:
		    print('error : incorrect size of elemens')
	#    print("elements size = " , elements_size, " bytes")
		f.write(struct.pack(format_string + 'b', elements_size ))
		_descriptor_length -= 1
	#################################################################################################################
		#check shape
		if (len(data_array.shape) == 1):
		    f.write(struct.pack(format_string+'b', 1))
		elif (len(data_array.shape) == 2):
		    if not (if_symmetric_matrix):
		        if (order_of_data =='F'):
		            f.write(struct.pack(format_string+'b', 22))
		        elif (order_of_data == 'C'):
		            f.write(struct.pack(format_string+'b', 21))
		    else:
		        if (order_of_data =='F'):
		            f.write(struct.pack(format_string+'b', 32))
		        elif (order_of_data == 'C'):
		            f.write(struct.pack(format_string+'b', 31))
		elif (len(data_array.shape) > 2):
		    f.write(struct.pack(format_string+'b', 40+len(data_array.shape)))

		_descriptor_length -= 1
		if printout:
		    print(order_of_data)
		#write the byte ordering
		f.write(struct.pack(format_string+'b', bo))
	#################################################################################################################
		#write the dimensions
		if (not if_symmetric_matrix):
		    for i in dims:
		        f.write(struct.pack(format_string+'i', i))
		        _descriptor_length -= 4
		else:
		    f.write(struct.pack(format_string+'i', dims[0]))
		    _descriptor_length -= 4
		if printout:
		    print(dims)

	#    print("need to shift", _descriptor_length)
		#fill the shift to 32 bytes
		_descriptor_length -= 1
		for i in range(_descriptor_length):
		    f.write(struct.pack(format_string+'b', -1))
		    _descriptor_length-=1
	#################################################################################################################
		#WRITE THE DATA
		if (not if_symmetric_matrix):
		    data_to_write = 1
		    for i in dims:
		        data_to_write *= i
		    data_array = data_array.reshape(data_to_write, order=order_of_data)
		    for i in data_array:
		        f.write(struct.pack(format_string+el_type, i))

		if (len(dims)==2) and if_symmetric_matrix:
		    for i in range(dims[0]):
		        for j in range(dims[1]):
		            if (order_of_data == 'C'):
		                if (i>=j):
		                    f.write(struct.pack( format_string+el_type, data_array[i,j]))
		            else:
		                if (j>=i):
		                    f.write(struct.pack( format_string+el_type, data_array[j,i]))
		return 0

# MolMod module
#
# Andriy Zhugayevych (azh@ukr.net), Sergei Matveev(matseralex@yandex.ru)
# www.zhugayevych.me/python/MolMod/index.htm
# created 20.08.2014, modified 5.11.2016

import os
import numpy
import sys


class MolMod:


# Change these parameters:

  xout=".out" # default extension for output files of all external programs (Gaussian, MOPAC, TINKER etc.)
  gau_xinp=".gau" # default extension for Gaussian input files
  gau_fld="gaussian/" # default directory for Gaussian input and output files on a remote machine
  gau_pbs="gaussian/_pbs" # pbs script for Gaussian job submission, see example here http://zhugayevych.me/soft/gaussian/_pbs
  gau_readdump="bin/readdump" # a utility reading Gaussian chk- and rwf-files, see http://zhugayevych.me/soft/gaussian/readdump.f90



###########################################################################
  ssh = ''

###########################################################################
  def setup(self, xout="", gau_xinp="", gau_fld="", gau_pbs="", gau_readdump="" ):
    if xout:
      self.xout=xout
    if gau_xinp:
      self.gau_xinp=gau_xinp
    if gau_fld:
      self.gau_fld=gau_fld
    if gau_pbs:
      self.gau_pbs=gau_pbs
    if gau_readdump:
      self.gau_readdump=gau_readdump


###########################################################################
  def ReadXYZ(self, filename, tags=[], printout = False, matrix_storage=False):
    xyz_file= open(filename)
    xyz_lines = xyz_file.readlines()
    Number_of_atoms = int(xyz_lines[0])
    atoms_list = []
    if matrix_storage:
      coord_matrix = numpy.zeros([Number_of_atoms, 3])
    i=0
    final_data=[]
    for xyz_line in xyz_lines:
      data = xyz_line.split()
      if (len(data)==4) and (i>1):
        if matrix_storage:
          atoms_list.append(data[0])
          coord_matrix[i - 2, 0] = float(data[1])
          coord_matrix[i - 2, 1] = float(data[2])
          coord_matrix[i - 2, 2] = float(data[3])
        else:
          if i < len(tags):
            final_data.append([data[0], numpy.asarray([float(data[1]), float(data[2]), float(data[3])]), tags[i]])
          else:
            final_data.append([data[0], numpy.asarray([float(data[1]), float(data[2]), float(data[3])])])
      i+=1
    if matrix_storage:
      final_data = [atoms_list, coord_matrix, tags]
    if printout:
      print(final_data)
    del xyz_lines
    xyz_file.close()
    return final_data
###########################################################################
  def ReadAtoms(self, filename, printout=False ):
    lines=open(filename,"r").readlines()
    l=len(lines)-1
    while l>0 and not(" Standard orientation:" in lines[l]): l=l-1
    if l==0: raise Warning("No coordinates are found in "+filename)
    if printout: print("The coordinates in standard orientation are found in line",l)
    # Conversion section
    Atoms=[]
    for line in lines[l+5:]:
      if line[:5]==" ----": break
      words=line.split()
      Atoms.append([self.dictionary[int(words[1])],numpy.asarray([ float(words[3]), float(words[4]), float(words[5])]) ])
    return Atoms

##############################################################################################
  def WriteXYZ (self, output_file, data, matrix_storage=False, printout=False, overwrite=False ):
    if os.path.isfile(output_file) and not(overwrite): raise Warning('File exists: '+output_file)
    start = 0
    end = 0
    geometry = open(output_file,"w")
    if printout:
      print("opened file")
    # Read the original file

    if matrix_storage:
      print("%d\nIn this line you can put comments" %(data[1].shape[0]), file=geometry)
      for i in range(data[1].shape[0]):
        print("%s %s %s %s" % (data[0][i] , data[1][i,0], data[1][i,1], data[1][i,2]), file=geometry) #write geometry in xyz format

    else:
      print("%d\nIn this line you can put comments" %(len(data)), file=geometry)
      for i in data:
        print("%s %s %s %s" % (i[0] , i[1][0], i[1][1], i[1][2]), file=geometry) #write geometry in xyz format

    if printout:
      print("written the data")

    geometry.close()

    if printout:
        print("finished sucsessfully")


###############################################################################################
  def SubmitJob(self, filename, q="", ppn=1, tag="", mem=5, after="", test=False, printout = False, overwrite = False):
    filename_without_path = filename.split('/')[len(filename.split('/'))-1]
    if self.ssh.fexists(self.gau_fld+filename_without_path):
      print('job with this name exists')
      if overwrite:
        print('overwrite it')
      else:
        print('stop')
        return

    local_f = open(filename,'r')
    f_lines = local_f.readlines()
    # Check nproc and mem
    i = 0
    if_finish = 0
    if_nproc = False
    if_mem = False
    while ('%' in f_lines[i]) and (if_finish < 2):
      if 'nproc' in f_lines[i]:
        nproc_in_input_file = int(''.join(x for x in f_lines[i] if x.isdigit()))
        n_proc_line_number = i
        if_finish += 1
        if_nproc = True
      if 'mem' in f_lines[i]:
        mem_in_input_file = int(''.join(x for x in f_lines[i] if x.isdigit()))
        mem_line_number = i
        if_finish += 1
        if_mem = True
      i += 1
    
    if if_finish != 2:
      _i=0
      for line in f_lines:
        if '#' in line:
          break
        _i += 1
      if not if_nproc:
        f_lines.insert(_i, '%nproc='+str(ppn)+'\n')
      if not if_mem:
        f_lines.insert(_i, '%mem='+str(mem * ppn)+'GB\n')
    else:
      if nproc_in_input_file != ppn:
        if printout:
          print("correcting number of processors in input file")
      f_lines[n_proc_line_number] = "%nproc="+str(ppn)+'\n'
      if mem_in_input_file != (mem * ppn):
        if printout:
          print("correcting memory request in input file")
      f_lines[mem_line_number]="%mem="+str( mem * ppn )+'GB\n'
    # correct input if needed
    local_f.close()
    local_f = open(filename, 'w')
    local_f.writelines(f_lines)
    local_f.close()
    # check test and overwrite
    if not test:
      self.ssh.put(filename, self.gau_fld+filename_without_path)
    else:
      print("IT WAS TEST: corrected cluster request parameters only in local file")
    del f_lines
    #generate command
    
    command = ""
    command += "qsub " + self.gau_pbs + " -l nodes=1" + ":ppn=" + str(ppn)
    if tag:
      command += ":" + tag
    command +=" -N "+ filename_without_path.split('.')[0]
    print(command)
    #Check testing options before execution on the remote machine
    if test:
      print("IT WAS TEST")
      return 0
    else:
      self.ssh.run(command, printout)
    return 0
###############################################################################################
  def DownloadJob(self, filename, binout=[], keep=[], printout=False, overwrite=False):
    # Download Gaussian log-file
    # Extract required records from rwf-file using gau_readdump utility, download them, and delete from remote machine
    fn10=filename
    fn20=self.gau_fld+filename

    fn1=fn10+self.xout
    fn2=fn20+self.xout
    if os.path.isfile(fn1):
      print("File exists:"+fn1)
      if not (overwrite):
        print("cannot overwrite it!")
        return 0
      else:
        print("have to overwrite it following your choice")
    #self.ssh.run("unix2dos -q "+fn2)
    self.ssh.sget(fn2,fn1)
    if printout:
      print("done "+self.xout[1:])

    fn1=fn10+self.xout
    fn2=fn20+self.xout
    for ext in binout:
      fn1=fn10+"."+ext
      fn2=fn20+"."+ext
      print(fn1)
      print(fn2)
      print(self.gau_readdump+" "+fn20+".rwf "+fn2+" "+ext)
      self.ssh.run( self.gau_readdump+" "+fn20+".rwf "+fn2+" "+ext,printout)
      if os.path.isfile(fn1):
        print("File exists:"+fn1)
        if not (overwrite):
          print("cannot overwrite it!")
          return 0
        else:
          print("have to overwrite it following your choice")
      self.ssh.sget(fn2,fn1,keeplocal=True)
      if ext not in keep:
        self.ssh.run("rm -f "+fn2)
      if printout:
        print("done "+ext)

    for ext in [self.gau_xinp[1:],self.xout[1:],"chk","rwf"]:
      if ext not in keep:
        self.ssh.run("rm -f "+fn20+"."+ext)

    return 0

###############################################################################################
  def WriteInput(self, filename, Atoms, Q=0, mult=0, keyline="", title="", output=[], matrix_storage=False, printout=False):
    filenameonly=(filename.split('/')[-1]).split('.')[0]
    if mult==0:
      m=Q%2+1
    else:
      m=mult
    f = open(filename, 'w')
    if "chk" in output:
      print("%chk="+filenameonly+'.chk', file=f)
    if "rwf" in output:
      print("%rwf="+filenameonly+'.rwf', file=f)
    prefix="T" if "T" in output else "P" if "P" in output else ""
    print("#"+prefix+" "+keyline+"\n", file=f)
    if title=="":
      print("", file=f)
    else:
      print(title+"\n", file=f)
    print("%d %d"%(Q,m), file=f)
    if not matrix_storage:
      for Atom in Atoms:
        print(Atom[0], " %f %f %f"%(Atom[1][0], Atom[1][1], Atom[1][2]), file=f)
    else:
      for i in range(len(data[0])):
        print(Atoms[0][i], " %f %f %f"%(Atoms[1][i, 0], Atoms[1][i, 1], Atoms[1][i, 2]), file=f)
    print('\n', file=f)
    f.close()
    if printout:
      f = open(filename,'r')
      print(f.read())
    return 0

###############################################################################################
  def WriteLam(self, lam_filename, xyz_filename, Masses_list, Bounding_box, printout=False):
    Atoms = self.ReadXYZ(xyz_filename)
    f = open(lam_filename, 'w')
    
    atoms_type_list = []
    atoms_type = 0
    # The atomic types will be sorted by the same order as at the XYZ-file
    # So the i-th element of the list corresponds to N-th atom type as a string with the name of atom
    # E.g. if atoms_type_list = ['C', 'H'] then 'C' has the atom type 1 and 'H' has the atom type 2
    for i in range(len(Atoms)):
      if not (Atoms[i][0] in atoms_type_list):
        atoms_type = atoms_type + 1
        atoms_type_list.append(Atoms[i][0])
    
    print("Lammps sample input file\n", file=f)
    print("%d atoms\n"%(len(Atoms)), file=f)
    print("%d atoms types\n"%(atoms_type), file=f)
    print(" %f %f xlo xhi\n %f %f ylo yhi\n %f %f zlo zhi\n"%(Bounding_box[0][0], Bounding_box[0][1], #x boundaries
                                                                   Bounding_box[1][0], Bounding_box[1][1], #y boundaries
                                                                   Bounding_box[2][0], Bounding_box[2][1]), file=f) #z boundaries
    print("Masses\n", file=f)
    # Get the masses of atoms from the list with the atomic masses 
    for i in range(atoms_type):
      if Masses_list[i][0] in atoms_type_list:
        print("%d %f"%(atoms_type_list.index(Masses_list[i][0]) + 1, Masses_list[i][1]), file=f)
    print("\nAtoms\n", file=f)
    # print the geometry; 
    # Strusture is simple: number of atom, its type number, x_coord, y_coord, z_coord
    for i in range(len(Atoms)):
      print("%d %d %f %f %f"%(i + 1,  atoms_type_list.index(Atoms[i][0]) + 1, Atoms[i][1][0], 
                                                                                     Atoms[i][1][1],
                                                                                     Atoms[i][1][2]), file=f)
    #Set the zero initial velocities
    print("\n Velocities\n", file=f)
    for i in range(len(Atoms)):
      print("%d %d %f %f %f"%( i + 1,  atoms_type_list.index(Atoms[i][0]) + 1, 0.0, 0.0, 0.0), file=f)
    return 0

###############################################################################################
  dictionary = {
    1:  "H",     2: "He",
    3: "Li",  4: "Be",  5:  "B",  6:  "C", 7:  "N", 8:  "O", 9:  "F", 10: "Ne",
    11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar",
    19: "K", 20: "Ca",
    21: "Sc", 22: "Ti", 23: "V",  24: "Cr", 25: "Mn", 26: "Fe", 27: "Co", 28: "Ni", 29: "Cu", 30: "Zn",
    31: "Ga", 32: "Ge", 33: "As", 34: "Se", 35: "Br", 36: "Kr",
    37: "Rb", 38: "Sr",
    39: "Y", 40: "Zr", 41: "Nb", 42: "Mo", 43: "Tc", 44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd", 49: "In", 50: "Sn",
    51: "Sb", 52: "Te", 53: "I", 54: "Xe",
    55: "Cs", 56: "Ba",
    57: "La", 58: "Ce", 59: "Pr", 60: "Nd", 61: "Pm", 62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy", 67: "Ho", 68: "Er", 69: "Tm", 70: "Yb", 71: "Lu",
    72: "Hf", 73:"Hf",  74: "W", 75: "Re", 76: "Os", 77: "Ir", 78: "Pt", 79: "Au", 80: "Hg", 81: "Tl", 82: "Pb", 83: "Bi", 84: "Po", 85: "At", 86: "Rn",
    87: "Fr", 88: "Ra",
    89: "Ac", 90: "Th", 91: "Pa", 92: "U", 93: "Np", 94: "Pu", 95: "Am", 96: "Cm", 97: "Bk", 98: "Cf", 99: "Es", 100: "Fm", 101: "Md", 102: "No", 103: "Lr",
    104: "Rf", 105: "Db", 106: "Sg", 107: "Bh", 108: "Hs", 109: "Mt", 110: "Ds", 111: "Rg", 112: "Cn", 113: "Uut",
    114: "Fl", 115: "Uup", 116: "Lv", 117: "Uus", 118: "Uuo"
  }

# SSHTools module
#
# Andriy Zhugayevych (azh@ukr.net), Sergei Matveev(matseralex@yandex.ru)
# www.zhugayevych.me/python/SSHTools/index.htm
# created 21.08.2014, modified 19.11.2019

import paramiko
import os
import hashlib

class SSHTools:
  user=""; host=""; ppk=""; pbs=""; port=22
###############################################################################################
  def setup( self, profile="", user="", host="", ppk="", pbs="", port=22 ):
    if profile:
      if profile=="pardus":
        self.user="Andriy.Zhugayevych"
        self.host="pardus.skoltech.ru"
        self.ppk="C:/Users/azh/Sys/Internet/SSH/pardus/key2.ppk"
        self.pbs="MOAB"
      elif profile=="magnus":
        self.user="a.zhugayevych"
        self.host="10.30.16.168"
        self.ppk="C:/Users/azh/Sys/Internet/SSH/magnus/key2.ppk"
        self.pbs="SLURM"
      elif profile=="cmsVM":
        self.user="a.zhugayevych"
        self.host="10.30.16.165"
        self.ppk="C:/Users/azh/Sys/Internet/SSH/cmsVM/key2.ppk"
        self.pbs="SLURM"
      else:
        raise Warning("Unrecognized profile")
    else:
      if user:
        self.user = user
      if host:
        self.host = host
      if ppk:
        self.ppk = ppk
      if pbs:
        self.pbs = pbs
    self.port = port
    self.ssh = paramiko.SSHClient()
    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.pkey = paramiko.RSAKey.from_private_key_file(self.ppk)
    return
###############################################################################################
  def run( self, command, noerror=False, printout=False ):
    if printout:
      print("command:",command)
    self.ssh.connect(self.host,username=self.user,pkey=self.pkey,port=self.port)
    stdin,stdout,stderr = self.ssh.exec_command(command)
    out=stdout.readlines()
    err=stderr.readlines()
    self.ssh.close()
    if err:
      if noerror:
        if printout:
          print("stderr:","".join(err))
        return err
      else:
        raise Warning("stderr: "+"".join(err))
    if printout:
      if len(out)==1:
        print("output:",out[0].rstrip())
      else:
        print("output:")
        for s in out:
          print(s.rstrip())
    return ("".join(out)).strip()
###############################################################################################
  def qstat( self ):
    if self.pbs=="MOAB":
      s=self.run( "qstat -u "+self.user, printout=True )
    if self.pbs=="SLURM":
      s=self.run( "squeue -u "+self.user, printout=True )
    return
###############################################################################################
  def put( self, source, dest ):
    self.ssh.connect(self.host,username=self.user,pkey=self.pkey,port=self.port)
    sftp = self.ssh.open_sftp()
    sftp.put(source,dest)
    sftp.close()
    self.ssh.close()
    return
###############################################################################################
  def get( self, source, dest ):
    self.ssh.connect(self.host,username=self.user,pkey=self.pkey,port=self.port)
    sftp = self.ssh.open_sftp()
    sftp.get(source,dest)
    sftp.close()
    self.ssh.close()
    return
###############################################################################################
  def sget( self, source, dest, keeplocal=False ):
    self.ssh.connect(self.host,username=self.user,pkey=self.pkey,port=self.port)
    sftp = self.ssh.open_sftp()
    sftp.get(source,dest)
    sftp.close()
    self.ssh.close()
    s=self.run("md5sum "+source)
    md5_remote=str(s).split()[0]
    md5_local=hashlib.md5(open(dest,'rb').read()).hexdigest()
    if md5_local!=md5_remote:
      print("md5 sums are different for",source,"and",dest,": ",md5_remote,"!=",md5_local)
      if not(keeplocal):
        os.remove(dest)
        print("Local copy is removed")
      raise Warning("Checksum error")
    return 0
###############################################################################################
  def fexists(self, filename):
#    return isinstance ( self.run ("ls "+ filename, noerror=True), str)
    return filename == self.run("ls " + filename, noerror = True)

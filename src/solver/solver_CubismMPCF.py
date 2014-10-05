
# # # # # # # # # # # # # # # # # # # # # # # # # #
# CubismMPCF solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === Discretization format:
# discretization = {'NX' : ?, 'NY' : ?, 'NZ' : ?, 'NS' : ?}

from solver import Solver
import os, subprocess
import local

class Example_Solver (Solver):
  
  def __init__ (self, options, cluster=0, bs=32):
    
    self.options = options
    self.cluster = cluster
    self.bs = bs
    
    args = '-name %(name)s -bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d %(options)s'
    self.cmd_node    = 'mpcf-node ' + args
    self.cmd_cluster = 'mpcf-cluster ' + args + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher'
    
    self.filename = 'output_%(name)s'
    self.indicator = lambda x : x
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ'] * d['NS']
  
  def validate (self, discretization, options, multi):
    
    if discretization ['NX'] < self.bs:
      print ' :: ERROR: mesh resolution NX is smaller than block size: %d < %d.' % ( discretization ['NX'], self.bs )
      print ' :: ERROR: mesh resolution NY is smaller than block size: %d < %d.' % ( discretization ['NY'], self.bs )
      print ' :: ERROR: mesh resolution NZ is smaller than block size: %d < %d.' % ( discretization ['NZ'], self.bs )
  
  def run (self, level, type, sample, id, discretization, options, multi):
    
    args = {}
    args ['name'] = self.name (level, type, sample, id)
    
    args ['bpdx'] = discretization ['NX'] / self.bs
    args ['bpdy'] = discretization ['NY'] / self.bs
    args ['bpdz'] = discretization ['NZ'] / self.bs
    
    args ['options'] = self.options
    
    if self.cluster:
      xpesize = multi ** 1/3
      ypesize = multi ** 1/3
      zpesize = multi ** 1/3
      args ['bpdx'] /= xpesize
      args ['bpdy'] /= ypesize
      args ['bpdz'] /= zpesize
      args ['xpesize'] = xpesize
      args ['ypesize'] = ypesize
      args ['zpesize'] = zpesize
    
    outputf = open (self.filename % args, 'w')
    
    if self.cluster:
      subprocess.check_call ( self.cmd_cluster % args, stdout=outputf, stderr=subprocess.STDOUT, shell=True )
    else:
      subprocess.check_call ( self.cmd_node    % args, stdout=outputf, stderr=subprocess.STDOUT, shell=True )
    
    #subprocess.check_call ( self.cmd, stdout=outputf, stderr=subprocess.STDOUT )
  
  def finished (self, level, type, sample, id):
    
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    return os.path.exists ( filename )
  
  def load (self, level, type, sample, id):
    
    if not self.finished (level, type, sample, id):
      Exception ( ' :: ERROR: sample %d form level %d of type %d could not be loaded (id is %d) !' % (level, type, sample, id) )
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    f = open ( filename, 'r' )
    from numpy.random import seed, randn
    seed ( self.pair ( self.pair (level, type), self.pair (sample, id) ) )
    f.close()
    return randn() / ( 2 ** level )

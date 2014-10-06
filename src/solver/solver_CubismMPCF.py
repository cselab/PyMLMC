
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
import os, subprocess, shutil
import local

class CubismMPCF (Solver):
  
  def __init__ (self, options, path=None, bs=32):
    
    self.options = options
    self.bs = bs
    
    if local.cluster:
      self.executable = 'mpcf-cluster'
    else:
      self.executable = 'mpcf-node'
    
    args = '-name %(name)s -bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d'
    
    if local.cluster:
      self.cmd = './' + self.executable + ' ' + args + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher'
    else:
      self.cmd = self.executable + ' ' + args
    
    self.filename = 'output_%(name)s'
    self.indicator = lambda x : x
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ'] * d['NS']
  
  # return the approproate ratio of the number of cores between two discretizations
  def ratio (self, d1, d2):
    
    return d1 ['NX'] / d2 ['NX'] * d1 ['NY'] / d2 ['NY'] * d1 ['NZ'] / d2 ['NZ']
  
  def validate (self, discretization, parallelization):
    
    # check if number of cells in not smaller than block size
    ranks = parallelization.cores / local.threads
    multi = ranks ** 1/3
    if discretization ['NX'] < self.bs * multi:
      print ' :: ERROR: mesh resolution NX / multi is smaller than block size: %d < %d.' % ( discretization ['NX'] / multi, self.bs )
    if discretization ['NY'] < self.bs * multi:
      print ' :: ERROR: mesh resolution NY / multi is smaller than block size: %d < %d.' % ( discretization ['NY'] / multi, self.bs )
    if discretization ['NZ'] < self.bs * multi:
      print ' :: ERROR: mesh resolution NZ / multi is smaller than block size: %d < %d.' % ( discretization ['NZ'] / multi, self.bs )
  
  def run (self, level, type, sample, id, discretization, params, parallelization):
    
    args = {}
    args ['name'] = self.name (level, type, sample, id)
    
    args ['bpdx'] = discretization ['NX'] / self.bs
    args ['bpdy'] = discretization ['NY'] / self.bs
    args ['bpdz'] = discretization ['NZ'] / self.bs
    
    args ['options'] = self.options
    
    args ['threads'] = local.threads
    
    # cluster run
    if local.cluster:
      
      # compute number of ranks
      ranks = parallelization / local.threads
      
      # compute *pesizes
      args ['xpesize'] = ranks ** 1/3
      args ['ypesize'] = ranks ** 1/3
      args ['zpesize'] = ranks ** 1/3
      
      # adjust bpd*
      args ['bpdx'] /= args ['xpesize']
      args ['bpdy'] /= args ['ypesize']
      args ['bpdz'] /= args ['zpesize']
      
      # assemble arguments for job submission
      submit_args ['job']               = local.run % { 'cmd' : self.cmd % args }
      submit_args ['ranks']             = ranks
      submit_args ['threads']           = local.threads
      submit_args ['cores']             = self.multi
      submit_args ['walltime-hours']    = self.walltime_hours
      submit_args ['walltime-minutes']  = seld.walltime_minutes
      submit_args ['memory']            = self.memory
      cmd = local.submit % submit_args
      
      # copy executable to present working directory
      if self.path:
        shutil.copy (self.path + self.executable, '.')
    
    # node run
    else:
      
      cmd = local.run % { 'cmd' : self.cmd % args }
    
    outputf = open (self.filename % args, 'w')
    subprocess.check_call ( cmd, stdout=outputf, stderr=subprocess.STDOUT, shell=True )
  
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

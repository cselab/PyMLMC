
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
    self.path = path
    self.bs = bs
    
    if local.cluster:
      self.executable = 'mpcf-cluster'
    else:
      self.executable = 'mpcf-node'
    
    args = '-name %(name)s -bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -nsteps %(steps)d -seed %(seed)d'
    
    if local.cluster:
      self.cmd = './' + self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher'
    else:
      self.cmd = self.executable + ' ' + args
    
    self.prefix = 'mpcf'
    
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
    multi = int ( ranks ** (1.0/3) )
    if discretization ['NX'] < self.bs * multi:
      print ' :: ERROR: mesh resolution NX / multi is smaller than block size: %d < %d.' % ( discretization ['NX'] / multi, self.bs )
    if discretization ['NY'] < self.bs * multi:
      print ' :: ERROR: mesh resolution NY / multi is smaller than block size: %d < %d.' % ( discretization ['NY'] / multi, self.bs )
    if discretization ['NZ'] < self.bs * multi:
      print ' :: ERROR: mesh resolution NZ / multi is smaller than block size: %d < %d.' % ( discretization ['NZ'] / multi, self.bs )
  
  def run (self, level, type, sample, id, seed, discretization, params, parallelization):
    
    args = {}
    
    args ['name']  = self.name  ( level, type, sample, id )
        
    args ['bpdx'] = discretization ['NX'] / self.bs
    args ['bpdy'] = discretization ['NY'] / self.bs
    args ['bpdz'] = discretization ['NZ'] / self.bs
    
    args ['steps'] = discretization ['NS']

    args ['options'] = self.options
    
    if parallelization.cores < local.threads:
      local.threads = parallelization.cores
    args ['threads'] = local.threads
    
    # cluster run
    if local.cluster:
      
      # compute number of ranks
      ranks = parallelization.cores / local.threads
      args ['ranks'] = ranks
      
      # compute *pesizes
      #TODO: increment *pesizes iteratively to allow powers of 2 instead of powers of 8 only ???
      # this, of course, would change the behaviour of the self.ratio()
      args ['xpesize'] = int ( ranks ** (1.0/3) )
      args ['ypesize'] = int ( ranks ** (1.0/3) )
      args ['zpesize'] = int ( ranks ** (1.0/3) )
      
      # adjust bpd*
      args ['bpdx'] /= args ['xpesize']
      args ['bpdy'] /= args ['ypesize']
      args ['bpdz'] /= args ['zpesize']
      
      # set seed
      args ['seed'] = seed
      
      # assemble excutable command
      args ['cmd'] = self.cmd % args
      
      # assemble job
      submit_args = {}
      if ranks > 1:
        submit_args ['job']               = local.mpi_job % args
      else:
        submit_args ['job']               = local.job % args
      
      # assemble arguments for job submission
      submit_args ['ranks']   = ranks
      submit_args ['threads'] = local.threads
      submit_args ['cores']   = parallelization.cores
      submit_args ['hours']   = parallelization.hours
      submit_args ['minutes'] = parallelization.minutes
      submit_args ['memory']  = local.memory
      submit_args ['label']   = self.label ( self.prefix, level, type, sample ) 
      
      # assemble submission command
      cmd = local.submit % submit_args
      
      # copy executable to present working directory
      if self.path:
        shutil.copy (self.path + self.executable, '.')
    
    # node run
    else:
      
      # assemble executable command
      args ['cmd'] = self.cmd % args
      
      # assemble job
      cmd = local.job % args
    
    with open ( os.devnull, 'w' ) as devnull:
      directory = os.getcwd () + '/' + args ['name']
      sys.mkdir ( directory )
      subprocess.check_call ( cmd, cwd=directory, stdout=devnull, stderr=subprocess.STDOUT, shell=True, env=os.environ.copy() )
  
  def finished (self, level, type, sample, id):
    
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    return os.path.exists ( filename )
  
  def load (self, level, type, sample, id):
    
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    f = open ( filename, 'r' )
    
    from numpy.random import seed, randn
    seed ( self.pair ( self.pair (level, type), self.pair (sample, id) ) )
    f.close()
    return randn() / ( 2 ** level )

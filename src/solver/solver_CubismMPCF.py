
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
import shutil
import local

class CubismMPCF (Solver):
  
  def __init__ (self, options, path=None, inputfiles=[], bs=32):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # set executable name
    if local.cluster:
      self.executable = 'mpcf-cluster'
    else:
      self.executable = 'mpcf-node'
    
    # set executable command template
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -nsteps %(steps)d -seed %(seed)d'
    if local.cluster:
      self.cmd = '../' + self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher'
    else:
      self.cmd = self.executable + ' ' + args
    
    # prefix for the labels
    self.prefix = 'mpcf'
    
    # set files and indicator
    self.statusfile = 'restart.status'
    self.outputfile = 'integrals.dat'
    self.indicator = lambda x : x [0]
    
    # copy executable to present working directory
    if local.cluster and self.path:
      shutil.copy (self.path + self.executable, '.')
  
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
    
    # node run
    else:
      
      # assemble executable command
      args ['cmd'] = self.cmd % args
      
      # assemble job
      cmd = local.job % args
    
    # get directory
    directory = self.directory ( level, type, sample, id )
    
    # report full submission command
    if params.verbose >= 1:
      print cmd
    
    # execute/submit job
    self.execute ( cmd, directory )
  
  def finished (self, level, type, sample, id):
    
     # get directory
    directory = self.directory ( level, type, sample, id )
    
    # open self.statusfile and check if both numbers are equal to 0
    statusfile = open ( directory + '/' + self.statusfile, 'r' )
    status = statusfile .read () .strip () .split ()
    statusfile.close()
    return ( float ( status[0] ) == 0 and float ( status [1] ) == 0 )
    #return os.path.exists ( self.statusfile )
  
  def load (self, level, type, sample, id):
    
    # NumPy style
    #data = numpy.loadtxt ( file, dtype={ 'names' : ('col1', 'col2', 'col3', 'col4'), 'formats' : ('S2', 'f4', 'f4', 'f4') } )
    #print data['FIP']
    
    # open self.outputfile, read and return results
    outputfile = open ( self.directory (level, type, sample, id) + '/' + self.outputfile, 'r' )
    lines = outputfile .readlines ()
    outputfile.close()
    return [ float ( line .strip() ) for line in lines ]

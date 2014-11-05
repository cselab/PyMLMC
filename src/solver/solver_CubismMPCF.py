
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

from solver import Solver, Results
import shutil
import local
import numpy
import sys

class CubismMPCF (Solver):
  
  def __init__ (self, options, inputfiles=[], path=None, points=5, bs=32, init=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # set executable name
    if local.cluster:
      self.executable = 'mpcf-cluster'
    else:
      self.executable = 'mpcf-node'
    
    # set path environment variable
    self.pathvar = 'MPCF_CLUSTER_PATH'
    
    # set default path
    self.setpath()
    
    # set executable command template
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -seed %(seed)d -nsteps %(nsteps)d'
    if local.cluster:
      self.cmd = '../' + self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher omp'
    else:
      self.cmd = self.executable + ' ' + args
    
    # prefix for the labels
    self.prefix = 'mpcf'
    
    # set datatype
    self.DataClass = Results
    
    # set files and indicator
    self.statusfile = 'restart.status'
    self.outputfile = 'integrals.dat'
    self.indicator = lambda x : x [ 'p_max' ] [ -1 ]
    
    # copy executable to present working directory
    if local.cluster and self.path:
      shutil.copy (self.path + self.executable, '.')
    
    # set default quantity of interest 'qoi'
    self.qoi = 'p_max'
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ'] * ( d['NX'] + d['NY'] + d['NZ'] )
  
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
    
    if 'NS' in discretization:
      args ['nsteps'] = discretization ['NS']
    else:
      args ['nsteps'] = 0
    
    args ['seed'] = seed
    
    args ['options'] = self.options
    
    args ['threads'] = min ( local.threads, parallelization.cores )
    
    # cluster run
    if local.cluster:
      
      # compute number of ranks
      ranks = max ( 1, parallelization.cores / local.threads )
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
      submit_args ['threads'] = args ['threads']
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
    
    # if specified, execute the initialization function
    if self.init:
      self.init ( args ['seed'] )
    
    # execute/submit job
    self.execute ( cmd, directory, params )
  
  def cloud (self):
    
    #TODO:
    print ' cloud() is not implemented'
  
  # TODO: this should be called only if local.cluster == 1
  def finished (self, level, type, sample, id):
    
    # for non-cluster machines, jobs are executed interactively
    # TODO: is this consistent with 'params.interactive'?
    if not local.cluster:
      return 1
    
    # get directory
    directory = self.directory ( level, type, sample, id )
    
    # TODO: open lsf.* file (rename to some status file?) and grep '<mpcf_0_0_0> Done'
    # open self.statusfile and check if both numbers are equal to 0
    #statusfile = open ( directory + '/' + self.statusfile, 'r' )
    #status = statusfile .read () .strip () .split ()
    #statusfile.close()
    return 1
    #return os.path.exists ( self.statusfile )
  
  def load (self, level, type, sample, id):
    
    # open self.outputfile and read results
    
    outputfile = open ( self.directory (level, type, sample, id) + '/' + self.outputfile, 'r' )
    from numpy import loadtxt
    
    names   = ( 'step', 't',  'dt', 'rInt', 'uInt', 'vInt', 'wInt', 'eInt', 'vol', 'ke', 'r2Int', 'mach_max', 'p_max', 'pow(...)', 'wall_p_max' )
    formats = ( 'i',    'f',  'f',  'f',    'f',    'f',    'f',    'f',    'f',   'f',  'f',     'f',        'f',     'f',        'f'          )
    meta_keys = ( 'step', 't',  'dt' )

    table = loadtxt ( outputfile, dtype = { 'names' : names, 'formats' : formats } )
    records = { name : table [name] for name in names }
    
    # split metadata from actual data
    
    results = Results ()
    for key in meta_keys:
      results.meta [key] = records [key]
      del records [key]
    results.data = records
    
    # interpolate time dependent results using linear interpolation
    # this is needed since number of time steps and time step sizes
    # are usually different for every deterministic simulation
    
    times = numpy.linspace ( results.meta ['t'] [0], results.meta ['t'] [-1], self.points + 1 )
    for key in results.data.keys():
      results.data [key] = numpy.interp ( times, results.meta ['t'], results.data [key], left=None, right=None )
    
    # update times
    
    results.meta ['it']  = times
    results.meta ['idt'] = numpy.diff (times)
    
    return results
    
    '''
    outputfile = open ( self.directory (level, type, sample, id) + '/' + self.outputfile, 'r' )
    lines = outputfile .readlines ()
    outputfile.close()
    return [ float ( line .strip() ) for line in lines ]
    '''

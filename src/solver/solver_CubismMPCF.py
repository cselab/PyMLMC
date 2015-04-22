
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
import local

import numpy
import sys
import os

class Interpolated_Time_Series (object):
  
  def __init__ (self):
    
    # somehow this is needed here --
    # otherwise I get non-empty dictionaries upon instantiation
    self.meta = {}
    self.data = {}
  
  def load_v1 (self, filename, meta_keys, data_keys, meta_formats, data_formats):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import loadtxt
    table = loadtxt ( outputfile, dtype = { 'names' : meta_keys + data_keys, 'formats' : meta_formats + data_formats } )
    records = dict ( (key, table [key]) for key in meta_keys + data_keys )
    
    outputfile.close()
    
    # split metadata from actual data
    
    for key in meta_keys:
      self.meta [key] = records [key]
      del records [key]
    self.data = records
  
  def load (self, filename, meta_keys):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import genfromtxt
    data = genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # split metadata from actual data
    
    for key in meta_keys:
      self.meta [key] = records [key]
      del records [key]
      self.data = records
  
  def interpolate (self, points):
    
    from numpy import linspace, interp
    
    times = linspace ( self.meta ['t'] [0], self.meta ['t'] [-1], points )
    for key in self.data.keys():
      self.data [key] = interp ( times, self.meta ['t'], self.data [key], left=None, right=None )
    
    self.meta ['t']  = times
  
  def init (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = []
      for step in xrange ( len ( a.data [key] ) ):
        self.data [key] .append ( 0 )
  
  def __iadd__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] += a.data [key] [step]
    return self
  
  def __isub__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] -= a.data [key] [step]
    return self
  
  def __str__ (self):
    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output

class CubismMPCF (Solver):
  
  def __init__ (self, options='', path=None, points=1000, bs=32, init=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # set executable name
    if local.cluster:
      self.executable = 'mpcf-cluster'
    else:
      self.executable = 'mpcf-node'
    
    # set path to the executable
    if not path: self.path = self.env ('MPCF_CLUSTER_PATH')
    
    # set executable command template
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -seed %(seed)d -ncores %(cpucores)d -restart %(proceed)d'
    if local.cluster:
      self.cmd = self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher omp'
    else:
      self.cmd = self.executable + ' ' + args
    
    # name of this solver (used as prefix for the job names)
    self.name = 'mpcf'
    
    # set datatype that function self.load(...) returns
    self.DataClass = Interpolated_Time_Series
    
    # enable shared memory (i.e. 1 MPI-rank per node)
    self.sharedmem = 1
    
    # set files, default quantity of interest, and indicator
    self.outputfile = 'statistics.dat'
    self.outputfile_v1 = 'integrals.dat'
    self.qoi = 'p_max'
    self.indicator = lambda x : numpy.max ( x [ 'p_max' ] )
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ'] * ( d['NX'] + d['NY'] + d['NZ'] )
  
  # return the prefered ratio of the number of cores between two discretizations
  def ratio (self, d1, d2):
    
    return d1 ['NX'] / d2 ['NX'] * d1 ['NY'] / d2 ['NY'] * d1 ['NZ'] / d2 ['NZ']
  
  # validate the proposed parallelization for the specified discretization
  def validate (self, discretization, parallelization):
    
    # get parallelization configuration
    xpesize, ypesize, zpesize = parallelization.reshape (3)
    
    # check if number of cells in not smaller than block size
    if discretization ['NX'] < self.bs * xpesize:
      print ' :: ERROR: mesh resolution NX / xpesize is smaller than block size: %d < %d.' % ( discretization ['NX'] / xpesize, self.bs )
      sys.exit()
    if discretization ['NY'] < self.bs * ypesize:
      print ' :: ERROR: mesh resolution NY / ypesize is smaller than block size: %d < %d.' % ( discretization ['NY'] / ypesize, self.bs )
      sys.exit()
    if discretization ['NZ'] < self.bs * zpesize:
      print ' :: ERROR: mesh resolution NZ / zpesize is smaller than block size: %d < %d.' % ( discretization ['NZ'] / zpesize, self.bs )
      sys.exit()
  
    # check if number of blocks is not smaller than available threads
    blocks_x = discretization ['NX'] / self.bs
    blocks_y = discretization ['NY'] / self.bs
    blocks_z = discretization ['NZ'] / self.bs
    blocks   = blocks_x * blocks_y * blocks_z
    if blocks < parallelization.threads:
      print ' :: ERROR: number of blocks is smaller than available threads: %d < %d.' % ( blocks, parallelization.threads )
      sys.exit()
  
  # run the specified deterministic simulation (level, type, sample)
  # note, that current contents of the 'input' directory (if exists) will be copied to the working directory
  def run (self, level, type, sample, seed, discretization, params, parallelization):
    
    # initialize arguments for the specified parallelization
    #TODO: move this to Scheduler base class?
    args = self.args (parallelization)
    
    # === set additional arguments
    
    args ['bpdx'] = discretization ['NX'] / self.bs
    args ['bpdy'] = discretization ['NY'] / self.bs
    args ['bpdz'] = discretization ['NZ'] / self.bs
    
    '''
    if 'NS' in discretization:
      args ['nsteps'] = discretization ['NS']
    else:
      args ['nsteps'] = 0
    '''
    
    args ['seed'] = seed
    
    args ['proceed'] = params.proceed
    
    # cluster run
    if local.cluster:
      
      # compute *pesizes
      args ['xpesize'], args ['ypesize'], args ['zpesize'] = parallelization.reshape (3)
      
      # adjust bpd*
      args ['bpdx'] /= args ['xpesize']
      args ['bpdy'] /= args ['ypesize']
      args ['bpdz'] /= args ['zpesize']
    
    # execute/submit job
    self.launch (args, parallelization, level, type, sample)
  
  def load (self, level, type, sample):
    
    # open self.outputfile and read results
    
    outputfile = os.path.join ( self.directory (level, type, sample), self.outputfile )
    outputfile_v1 = os.path.join ( self.directory (level, type, sample), self.outputfile_v1 )
    if os.path.exists (outputfile):
      version = 2
    elif os.path.exists (outputfile_v1):
      version = 1
    else:
      print
      print ' :: ERROR: Output file does not exist (version 1.0 also absent):'
      print '  : %s' % outputfile
      print
      sys.exit()
    
    results = Interpolated_Time_Series ()
    
    # meta data
    meta_keys    = ( 'step', 't',  'dt' )
    
    # version 1.0 (integrals.dat)
    if version == 1:
      
      meta_formats = ( 'i',    'f',  'f'  )
      data_keys    = ( 'r_avg', 'u_avg', 'v_avg', 'w_avg', 'p_avg', 'V2', 'ke_avg', 'r2_int', 'M_max', 'p_max', 'Req', 'pw_max', 'kin_ke', 'r_min', 'p_min' )
      data_formats = ( 'f', ) * len (data_keys)
      results .load_v1 ( outputfile_v1, meta_keys, data_keys, meta_formats, data_formats )
    
    # version 2.0 (statistics.dat)
    else:
      
      results .load ( outputfile, meta_keys )
    
    # for non-deterministic simulations,
    # interpolate time dependent results using linear interpolation
    # this is needed since number of time steps and time step sizes
    # are usually different for every simulation
    if not self.deterministic:
      
      results .interpolate ( self.points + 1 )
      
      # compute meta parameters for interpolation
      results.meta ['dt'] = numpy.diff (results.meta['t'])
    
    return results

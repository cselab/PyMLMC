
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
  
  def load_v1 (self, filename, meta_keys, data_keys, meta_formats, data_formats):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import loadtxt
    data = loadtxt ( outputfile, dtype = { 'names' : meta_keys + data_keys, 'formats' : meta_formats + data_formats } )
    records = dict ( (key, data [key]) for key in meta_keys + data_keys )
    
    outputfile.close()
    
    # split metadata from actual data
    
    for key in meta_keys:
      self.meta [key] = records [key]
      del records [key]
    self.data = records
  
  def append_v1 (self, filename, meta_keys, data_keys, meta_formats, data_formats):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import loadtxt
    data = loadtxt ( outputfile, dtype = { 'names' : meta_keys + data_keys, 'formats' : meta_formats + data_formats } )
    records = dict ( (key, data [key]) for key in meta_keys + data_keys )
    
    outputfile.close()
    
    # array of NaN's for filling the gaps
    
    count = len (records.values() [0])
    nan_array = numpy.empty ( (count, 1) )
    nan_array [:] = numpy.NAN
    
    # append metadata
    
    for key in meta_keys:
      if key in self.meta.keys():
        self.meta [key] = numpy.hstack ( self.meta [key], records [key] )
    
    # append data
    
    for key in data_keys:
      if key in self.data.keys():
        self.data [key] = numpy.hstack ( self.data [key], records [key] )

    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta_keys:
        self.meta [key] = numpy.hstack ( self.meta [key], nan_array )
  
    # fill in remaining data

    for key in self.data.keys():
      if key not in data_keys:
        self.data [key] = numpy.hstack ( self.data [key], nan_array )
  
  def append_v2 (self, filename, meta_keys):

    outputfile = open ( filename, 'r' )
    
    from numpy import genfromtxt
    data = genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # split metadata from actual data
    
    meta = {}
    for key in meta_keys:
      meta [key] = records [key]
      del records [key]
    
    # array of NaN's for filling the gaps
    
    count = len (records.values()[0])
    nan_array = numpy.empty ( (count, 1) )
    nan_array [:] = numpy.NAN
    
    # append metadata
    
    for key in meta.keys():
      if key in self.meta.keys():
        self.meta [key] = numpy.hstack ( self.meta [key], meta [key] )
    
    # append data
    
    for key in records.keys():
      if key in self.data.keys():
        self.data [key] = numpy.hstack ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta.keys():
        self.meta [key] = numpy.hstack ( self.meta [key], nan_array )

    # fill in remaining data

    for key in self.data.keys():
      if key not in records.keys():
        self.data [key] = numpy.hstack ( self.data [key], nan_array )
  
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
    self.outputfile    = 'statistics.dat'
    self.outputfile_v2 = 'statistics_legacy.dat'
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
    
    outputfile    = os.path.join ( self.directory (level, type, sample), self.outputfile    )
    outputfile_v1 = os.path.join ( self.directory (level, type, sample), self.outputfile_v1 )
    outputfile_v2 = os.path.join ( self.directory (level, type, sample), self.outputfile_v2 )
    if os.path.exists (outputfile):
      version = 3
    elif os.path.exists (outputfile_v2):
      version = 2
    elif os.path.exists (outputfile_v1):
      version = 1
    else:
      print
      print ' :: ERROR: Output file does not exist (versions 1.0 and 2.0 also absent):'
      print '  : %s' % outputfile
      print
      sys.exit()
    
    results = Interpolated_Time_Series ()
    
    # meta data
    meta_keys    = ( 'step', 't',  'dt' )
    meta_formats = ( 'i',    'f',  'f'  )
    data_keys    = ( 'r_avg', 'u_avg', 'v_avg', 'w_avg', 'p_avg', 'V2', 'ke_avg', 'r2_avg', 'M_max', 'p_max', 'Req', 'pw_max', 'kin_ke', 'r_min', 'p_min' )
    data_formats = ( 'f', ) * len (data_keys)
    
    # version 1.0 (only iself.outputfile_v1 exists)
    if version == 1:
      results .load_v1 ( outputfile_v1, meta_keys, data_keys, meta_formats, data_formats )
    
    # version 3.0 (self.outputfile exists)
    else:
      results .load ( outputfile, meta_keys )
      
      # append version 2.0 to version 3.0 (self.outputfile_v2 also exists)
      if os.path.exists (outputfile_v2):
        results .append_v2 ( outputfile_v2, meta_keys )
      
      # append version 1.0 to version 3.0 (self.outputfile_v1 also exists)
      if os.path.exists (outputfile_v1):
        results .append_v1 ( outputfile_v1, meta_keys, data_keys, meta_formats, data_formats )
    
    # for non-deterministic simulations
    if not self.deterministic:
      
      # interpolate time dependent results using linear interpolation
      # this is needed since number of time steps and time step sizes
      # are usually different for every simulation
      results .interpolate ( self.points + 1 )
      
      # compute meta parameters for interpolation
      results.meta ['dt'] = numpy.diff (results.meta['t'])
    
    return results

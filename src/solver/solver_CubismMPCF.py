
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
import helpers

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
  
  def append (self, filename, meta_keys):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import genfromtxt
    data = genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # filter out existing entries
    
    positions = []
    for position, step in enumerate (records ['step']):
      if step in self.meta ['step']:
        positions .append (position)
    for key in records.keys():
      records [key] = numpy.delete ( records [key], positions )
    
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
        self.meta [key] = numpy.append ( self.meta [key], meta [key] )
    
    # append data
    
    for key in records.keys():
      if key in self.data.keys():
        self.data [key] = numpy.append ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], nan_array )

    # fill in remaining data

    for key in self.data.keys():
      if key not in records.keys():
        self.data [key] = numpy.append ( self.data [key], nan_array )
  
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
    
    # filter out existing entries
    
    positions = []
    for position, step in enumerate (records ['step']):
      if step in self.meta ['step']:
        positions .append (position)
    for key in records.keys():
      records [key] = numpy.delete ( records [key], positions )
    
    # kinetic energy fix
    
    extent = 20
    #extent = 40
    records ['ke_avg'] /= float (extent) ** 3
    records ['ke_avg'] *= 61
    #records ['ke_avg'] *= 344
    
    # array of NaN's for filling the gaps
    
    count = len (records.values() [0])
    nan_array = numpy.empty ( (count, 1) )
    nan_array [:] = numpy.NAN
    
    # append metadata
    
    for key in meta_keys:
      if key in self.meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], records [key] )
    
    # append data
    
    for key in data_keys:
      if key in self.data.keys():
        self.data [key] = numpy.append ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta_keys:
        self.meta [key] = numpy.append ( self.meta [key], nan_array )
    
    # fill in remaining data
    
    for key in self.data.keys():
      if key not in data_keys:
        self.data [key] = numpy.append ( self.data [key], nan_array )
  
  def append_v2 (self, filename, meta_keys):

    outputfile = open ( filename, 'r' )
    
    from numpy import genfromtxt
    data = genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # filter out existing entries
    
    positions = []
    for position, step in enumerate (records ['step']):
      if step in self.meta ['step']:
        positions .append (position)
    for key in records.keys():
      records [key] = numpy.delete ( records [key], positions )
    
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
        self.meta [key] = numpy.append ( self.meta [key], meta [key] )
    
    # append data
    
    for key in records.keys():
      if key in self.data.keys():
        self.data [key] = numpy.append ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], nan_array )

    # fill in remaining data

    for key in self.data.keys():
      if key not in records.keys():
        self.data [key] = numpy.append ( self.data [key], nan_array )
  
  # filter out duplicate entries (keep the first occurrence only)
  def unique (self, key):
    
    # obtain positions of duplicate entries
    positions = []
    values    = []
    for position, value in enumerate (self.meta ['step']):
      if value in values:
        positions .append (position)
      else:
        values .append (value)
    
    # remove duplicate entries from metadata
    for key in self.meta.keys():
      self.meta [key] = numpy.delete ( self.meta [key], positions )
    
    # remove duplicate entries from data
    for key in self.data.keys():
      self.data [key] = numpy.delete ( self.data [key], positions )
  
  def sort (self, key):
    
    # obtain sorting order
    order = numpy.argsort (self.meta [key])

    # sort metadata
    for key in self.meta.keys():
      self.meta [key] = self.meta [key] [order]
    
    # sort data
    for key in self.data.keys():
      self.data [key] = self.data [key] [order]

  def interpolate (self, points, begin=None, end=None):
    
    from numpy import linspace, interp
    if begin == None: begin = self.meta ['t'] [0]
    if end   == None: end   = self.meta ['t'] [-1]
    
    times = linspace ( begin, end, points )
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
  
  def __init__ (self, options='', path=None, points=1000, bs=32, workunit=1, init=None):
    
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
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -spongewidth %(spongewidth)d -seed %(seed)d -ncores %(cpucores)d -restart %(proceed)d'
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
    self.outputfile       = 'statistics.dat'
    self.outputfileformat = 'statistics*.dat'
    self.outputfile_v1    = 'integrals.dat'
    self.qoi = 'p_sen1'
    self.indicator = lambda x : numpy.max ( x [ 'p_sen1' ] )
  
  # return string representing the resolution of a give discretization 'd'
  def resolution_string (self, d):
    from helpers import intf
    if d ['NX'] == d ['NY'] and d ['NX'] == d ['NZ']:
      return intf (d['NX']) + '^3'
    else:
      return intf (d['NX']) + 'x' + intf (d['NY']) + 'x' + intf (d['NZ'])

  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return self.workunit * d ['NX'] * d ['NY'] * d ['NZ'] * numpy.max ( [ d['NX'], d['NY'], d['NZ'] ] )
  
  # return the prefered ratio of the number of cores between two discretizations
  def ratio (self, d1, d2):
    
    return d1 ['NX'] / d2 ['NX'] * d1 ['NY'] / d2 ['NY'] * d1 ['NZ'] / d2 ['NZ']
  
  # validate the proposed parallelization for the specified discretization
  def validate (self, discretization, parallelization):
    
    # get parallelization configuration
    xpesize, ypesize, zpesize = parallelization.reshape (3)
    
    # check if number of cells in not smaller than block size
    if discretization ['NX'] < self.bs * xpesize:
      message = 'mesh resolution NX / xpesize is smaller than block size'
      details = '%d / %d < %d.' % ( discretization ['NX'], xpesize, self.bs )
      helpers.error (message, details)
    if discretization ['NY'] < self.bs * ypesize:
      message = 'mesh resolution NY / ypesize is smaller than block size'
      details = '%d / %d < %d.' % ( discretization ['NY'], ypesize, self.bs )
      helpers.error (message, details)
    if discretization ['NZ'] < self.bs * zpesize:
      message = 'mesh resolution NZ / zpesize is smaller than block size'
      details = '%d / %d < %d.' % ( discretization ['NZ'], zpesize, self.bs )
      helpers.error (message, details)
    
    # check if number of blocks is not smaller than available threads
    blocks_x = discretization ['NX'] / (self.bs * xpesize)
    blocks_y = discretization ['NY'] / (self.bs * ypesize)
    blocks_z = discretization ['NZ'] / (self.bs * zpesize)
    blocks   = blocks_x * blocks_y * blocks_z
    if blocks < parallelization.threads:
      message = 'number of blocks is smaller than available threads: %d < %d.' % ( blocks, parallelization.threads )
      details = 'Discretization: %s' % str(discretization)
      advice  = 'Parallelization: %s ranks, %d threads' % ( str(parallelization.reshape(3)), parallelization.threads )
      helpers.warning (message, details, advice)
      helpers.query   ('Continue with sub-optimal parallelization?')
  
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
    
    args ['spongewidth'] = discretization ['spongewidth']
    
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
  
  def load (self, level=0, type=0, sample=0, file=None):
    
    # get all available output files for version 2.0
    from glob import glob
    if file:
      outputfiles = [self.root + file]
    else:
      outputfileformat = os.path.join ( self.directory (level, type, sample), self.outputfileformat )
      outputfiles = glob (outputfileformat)
    v2 = len (outputfiles) != 0
    
    # check for output file for version 1.0
    outputfile_v1 = os.path.join ( self.directory (level, type, sample), self.outputfile_v1 )
    v1 = os.path.exists (outputfile_v1)
    
    # check if any output files found
    if not v2 and not v1:
      if self.params.verbose >= 1:
        helpers.warning ('Output file does not exist (version 1.0 is also absent)', details = outputfileformat)
      raise Exception ('Output file does not exist')
    
    results = Interpolated_Time_Series ()
    
    # meta data
    meta_keys    = ( 'step', 't',  'dt' )
    meta_formats = ( 'i',    'f',  'f'  )
    data_keys    = ( 'r_avg', 'u_avg', 'v_avg', 'w_avg', 'p_avg', 'V2', 'ke_avg', 'r2_avg', 'M_max', 'p_max', 'Req', 'pw_max', 'kin_ke', 'r_min', 'p_min' )
    data_formats = ( 'f', ) * len (data_keys)
    
    # only version 1.0 available
    if v1 and not v2:
      results .load_v1 ( outputfile_v1, meta_keys, data_keys, meta_formats, data_formats )
    
    # version 2.0
    else:
      
      # load first output file
      results .load ( outputfiles [0], meta_keys )
      
      # append remaining output files
      for outputfile in outputfiles [1:]:
        results .append ( outputfile, meta_keys )
      
      # append version 1.0
      if v1:
        results .append_v1 ( outputfile_v1, meta_keys, data_keys, meta_formats, data_formats )
    
    # fix for run from MIRA - why this is needed?
    results .data ['ke_avg'] = numpy.abs (results .data ['ke_avg'])
    
    # correct time dimension
    results .meta ['t'] *= numpy.sqrt(10)
    base_qois = ['c', 'm', 'u', 'v', 'w', 'W']
    types = ['_avg', '_min', '_max']
    for base_qoi in base_qois:
      for type in types:
        qoi = base_qoi + type
        if qoi in results.data: results.data [qoi] /= numpy.sqrt(10)
    
    # filter out duplicate entries
    results.unique ('step')
    
    # sort results by time
    results.sort ('step')
    
    # for non-deterministic simulations
    if not self.deterministic:
      
      # interpolate time dependent results using linear interpolation
      # this is needed since number of time steps and time step sizes
      # are usually different for every simulation
      # TODO: if simulation is not yet finished, interpolation interval must be adapted!
      results .interpolate ( self.points + 1 )
      
      # compute meta parameters for interpolation
      results.meta ['dt'] = numpy.diff (results.meta ['t'])
    
    return results

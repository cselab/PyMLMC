
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

class CubismMPCF (Solver):
  
  def __init__ (self, tend, options='', qoi=None, path=None, name='mpcf', bs=32, workunit=None, init=None, indicator=None, distance=None, norm='max', dataclass=None):
    
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
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -tend %(tend)f -spongewidth %(spongewidth)d -seed %(seed)d -ncores %(cpucores)d -restart %(proceed)d %(options)s'
    if local.cluster:
      self.cmd = self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher omp'
    else:
      self.cmd = self.executable + ' ' + args
    
    # shared memory support (i.e. 1 MPI-rank per node)
    self.sharedmem = 1

    # default workunit
    if not workunit: self.workunit = 2 * tend * float (8192 * 16 * 24) / (4096 ** 4)

    '''
    # set files
    self.outputfile       = 'statistics.dat'
    self.outputfileformat = 'statistics*.dat'
    self.outputfile_v1    = 'integrals.dat'
    '''

    # set default dataclass
    if dataclass == None:
      from dataclass_series import Series
      self.dataclass = Series (qois = 'all', filename = 'statistics.dat', metaqois = ['step', 't'], uid = 't', span = [0, tend], sampling = 1000)

    # set default quantity of interest
    if not qoi:
      qois = { 'series' : 'p_sensor1', 'shells' : 'p', 'slice' : 'p', 'line' : 'p' }
      self.qoi = qois [self.dataclass.name]

    # set indicator
    if not self.indicator:

      # maximum-norm based indicator
      if self.norm == 'max':
        self.indicator = lambda data : numpy.max ( numpy.abs (data [self.qoi]) )

      # 1-norm based indicator
      if self.norm == 1:
        self.indicator = lambda data : numpy.mean ( numpy.abs (data [self.qoi]) )
      
    # set distance
    if not self.distance:

      if self.norm == 'max':
        self.distance = lambda f, c : self.indicator (f) - self.indicator (c) if c != None else self.indicator (f)
        #self.distance = lambda f, c : numpy.max ( numpy.abs (f [self.qoi]) - numpy.abs (c [self.qoi]) ) if c != None else self.indicator (f)
        #self.distance = lambda f, c : numpy.max ( f [self.qoi] [ ~ numpy.isnan (f [self.qoi]) ] ) - numpy.max ( c [self.qoi] [ ~ numpy.isnan (c [self.qoi]) ] ) if c != None else self.indicator (f)

      # 1-norm based distance
      if self.norm == 1:
        #self.distance = lambda f, c : numpy.mean ( numpy.abs ( numpy.array ( [ entry for entry in (f [self.qoi] - c [self.qoi]) if not numpy.isnan (entry) ] ) ) ) if c != None else self.indicator (f)
        self.distance = lambda f, c : numpy.mean ( numpy.abs ( (f - c) [self.qoi] ) ) if c != None else self.indicator (f)

  # return string representing the resolution of a given discretization 'd'
  def resolution_string (self, d):
    from helpers import intf
    if d ['NX'] == d ['NY'] and d ['NX'] == d ['NZ']:
      return intf (d['NX']) + '^3'
    else:
      return intf (d['NX']) + 'x' + intf (d['NY']) + 'x' + intf (d['NZ'])

  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ'] * numpy.max ( [ d['NX'], d['NY'], d['NZ'] ] )
  
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
    
    # get parallelization args
    args = parallelization.args()

    # === set additional arguments

    args ['bpdx'] = discretization ['NX'] / self.bs
    args ['bpdy'] = discretization ['NY'] / self.bs
    args ['bpdz'] = discretization ['NZ'] / self.bs

    args ['tend'] = self.tend
    
    args ['spongewidth'] = discretization ['spongewidth']

    args ['options']  = self.options
    
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

  def progress (self, results):

    time = numpy.max ( [ time for step, time in enumerate (results.meta ['t']) if not numpy.isnan (results.data [self.qoi] [step]) ] )
    return float (time) / self.tend

  def load (self, level=0, type=0, sample=0):
    
    # load results from the specified directory
    return self.dataclass.load ( self.directory (level, type, sample), self.params.verbose )

    # TODO: remove legacy code below
    '''
    # get all available output files for version 2.0
    from glob import glob
    if filename:
      outputfiles = [self.root + filename]
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
    
    results = Series ()
    
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
    #results .data ['ke_avg'] = numpy.abs (results .data ['ke_avg'])
    
    # correct time dimension
    #results .meta ['t'] *= numpy.sqrt(10)
    #base_qois = ['c', 'm', 'u', 'v', 'w', 'W']
    #types = ['_avg', '_min', '_max']
    #for base_qoi in base_qois:
    #  for type in types:
    #    qoi = base_qoi + type
    #    if qoi in results.data: results.data [qoi] /= numpy.sqrt(10)

    # filter out duplicate entries
    results.unique ('step')
    
    # sort results by time
    results.sort ('step')
    
    # for non-deterministic simulations
    if not self.deterministic:
      
      # interpolate time dependent results using linear interpolation
      # this is needed since number of time steps and time step sizes
      # are usually different for every simulation
      results .interpolate ( self.points + 1, begin=0, end=self.tend )
      #results .interpolate ( self.points + 1, begin=0, end=self.tend*numpy.sqrt(10) )

    return results
    '''

  def efficiency (self, level=0, type=0, sample=0, file=None):

    # set lookup prefix
    prefix = '[           STEP]:'

    # configure file
    if file == None:

      # get directory
      directory = self.directory ( level, type, sample )

      # use the 'timerfile'
      file = os.path.join (directory, self.timerfile)
    
    # parse the file
    efficiencies = []
    if os.path.exists (file):
      with open ( file, 'r' ) as f:
        lines = f.readlines()
        for line in lines:
          if line.startswith (prefix):
            tail = line [ len (prefix) : ]
            head = tail [ 0 : tail.index ('-') ]
            head = head.strip()
            try:
              efficiencies.append ( float (head) )
            except:
              efficiencies.append ( float ('nan') )

    # return the average
    if len (efficiencies) > 0:
      return numpy.mean (efficiencies)
    else:
      return None

  # check if the loaded result is invalid
  def invalid (self, results):
    
    '''
    if (results.data ['c_global_max'] > 100) .any() or (results.data ['c_global_max'] < 0.1) .any():
      return 1

    qois = [ 'c_global_max', 'p_global_max' ]
    for qoi in qois:
      if numpy.isnan (results.data [qoi]) .any() or numpy.isinf (results.data [qoi]) .any():
        return 1
    '''

    return 0






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
from dataclass import Interpolated_Time_Series
import local
import helpers

import numpy
import sys
import os

class CubismMPCF (Solver):
  
  def __init__ (self, tend, options='', path=None, name='mpcf', points=1000, bs=32, workunit=1, init=None, indicator=None, distance=None):
    
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
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -tend %(tend)f -spongewidth %(spongewidth)d -seed %(seed)d -ncores %(cpucores)d -restart %(proceed)d'
    if local.cluster:
      self.cmd = self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher omp'
    else:
      self.cmd = self.executable + ' ' + args
    
    # enable shared memory (i.e. 1 MPI-rank per node)
    self.sharedmem = 1
    
    # set files
    self.outputfile       = 'statistics.dat'
    self.outputfileformat = 'statistics*.dat'
    self.outputfile_v1    = 'integrals.dat'

    # set default quantity of interest
    self.qoi = 'p_sen1'

    # set indicator
    if not self.indicator:
      #self.indicator = lambda x : numpy.nanmax ( x.data ['p_sen1'] )
      self.indicator = lambda x : numpy.nanmean ( x.data ['p_sen1'] )

    # set distance
    if not self.distance:
      #self.distance = lambda f, c : numpy.abs ( numpy.nanmax (f.data ['p_sen1']) - numpy.nanmax (c.data ['p_sen1']) if c != None else numpy.nanmax (f.data ['p_sen1']) )
      self.distance = lambda f, c : numpy.nanmean ( numpy.abs ( f.data ['p_sen1'] - c.data ['p_sen1'] if c != None else f.data ['p_sen1'] ) )

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

    args ['tend'] = self.tend
    
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

  def progress (self, results):

    ts = [ t for step, t in enumerate (results.meta ['t']) if results.data [self.qoi] != None ]
    return max (ts)

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
      results .interpolate ( self.points + 1, begin=0, end=self.tend*numpy.sqrt(10) )
      
      # compute meta parameters for interpolation
      results.meta ['dt'] = numpy.diff (results.meta ['t'])
    
    return results

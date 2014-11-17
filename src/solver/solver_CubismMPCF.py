
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

class Interpolated_Time_Series (object):
  
  meta = {}
  data = {}
  
  def load (self, filename, names, formats, meta_keys):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import loadtxt
    table = loadtxt ( outputfile, dtype = { 'names' : names, 'formats' : formats } )
    records = { name : table [name] for name in names }
    
    outputfile.close()
    
    # split metadata from actual data
    
    for key in meta_keys:
      self.meta [key] = records [key]
      del records [key]
    self.data = records
  
  def interpolate (self, wrt, points):
    
    from numpy import linspace, interp
    
    times = linspace ( self.meta [wrt] [0], self.meta [wrt] [-1], points )
    for key in self.data.keys():
      self.data [key] = interp ( times, self.meta [wrt], self.data [key], left=None, right=None )
    
    self.meta [wrt + '_i']  = times
  
  def __iadd__ (self, a):
    if not self.data:
      self.zeros (a)
    print 'boo'
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] += a.data [key] [step]
    return self
  
  def __isub__ (self, a):
    if not self.data:
      self.zeros (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] -= a.data [key] [step]
    return self
  
  def zeros (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = []
      for step in xrange ( len ( a.data [key] ) ):
        self.data [key] .append ( 0 )
  
  def __str__ (self):
    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output

class CubismMPCF (Solver):
  
  def __init__ (self, options='', inputfiles=[], path=None, points=1000, bs=32, init=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # set executable name
    if local.cluster:
      self.executable = 'mpcf-cluster'
    else:
      self.executable = 'mpcf-node'
    
    # set path to the executable
    if not path: self.path = self.env('MPCF_CLUSTER_PATH')
    
    # set executable command template
    args = '-bpdx %(bpdx)d -bpdy %(bpdy)d -bpdz %(bpdz)d -seed %(seed)d -nsteps %(nsteps)d'
    if local.cluster:
      self.cmd = self.executable + ' ' + args + ' ' + '-xpesize %(xpesize)d -ypesize %(ypesize)d -zpesize %(zpesize)d -dispatcher omp'
    else:
      self.cmd = self.executable + ' ' + args
    
    # prefix for the job names
    self.prefix = 'mpcf'
    
    # set datatype that function self.load(...) returns
    self.DataClass = Interpolated_Time_Series
    
    # set files, default quantity of interest, and indicator
    self.outputfile = 'integrals.dat'
    self.qoi = 'p_max'
    self.indicator = lambda x : numpy.max ( x [ 'p_max' ] )
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ'] * ( d['NX'] + d['NY'] + d['NZ'] )
  
  # return the prefered ratio of the number of cores between two discretizations
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
    
    # initialize arguments for the specified parallelization
    #TODO: move this to Scheduler base class?
    args = self.args (parallelization)
    
    # === set additional arguments
    
    args ['bpdx'] = discretization ['NX'] / self.bs
    args ['bpdy'] = discretization ['NY'] / self.bs
    args ['bpdz'] = discretization ['NZ'] / self.bs
    
    if 'NS' in discretization:
      args ['nsteps'] = discretization ['NS']
    else:
      args ['nsteps'] = 0
    
    args ['seed'] = seed
    
    # cluster run
    if local.cluster:
      
      # compute *pesizes
      # increment *pesizes iteratively to allow ranks as powers of 2
      args ['xpesize'] = int ( numpy.floor (ranks ** (1.0/3) ) )
      args ['ypesize'] = int ( numpy.floor (ranks ** (1.0/3) ) )
      args ['zpesize'] = int ( numpy.floor (ranks ** (1.0/3) ) )
      if ranks % 2 == 0: args ['xpesize'] *= 2
      if ranks % 4 == 0: args ['ypesize'] *= 2
      
      # adjust bpd*
      args ['bpdx'] /= args ['xpesize']
      args ['bpdy'] /= args ['ypesize']
      args ['bpdz'] /= args ['zpesize']
    
    # assemble job
    # TODO: move this to Scheduler base class?
    cmd = assemble (self, paralellization, args)
    
    # get directory
    directory = self.directory ( level, type, sample, id )
    
    # if specified, execute the initialization function
    if self.init:
      self.init ( args ['seed'] )
    
    # execute/submit job
    self.execute ( cmd, directory, params )
  
  def finished (self, level, type, sample, id):
    
    # get directory
    directory = self.directory ( level, type, sample, id )
    
    # TODO: open lsf.* file (rename to some status file?) and grep '<mpcf_0_0_0> Done'
    return 1
    
  def load (self, level, type, sample, id):
    
    # open self.outputfile and read results
    
    outputfile = self.directory (level, type, sample, id) + '/' + self.outputfile
    
    names   = ( 'step', 't',  'dt', 'rInt', 'uInt', 'vInt', 'wInt', 'eInt', 'vol', 'ke', 'r2Int', 'mach_max', 'p_max', 'pow(...)', 'wall_p_max' )
    formats = ( 'i',    'f',  'f',  'f',    'f',    'f',    'f',    'f',    'f',   'f',  'f',     'f',        'f',     'f',        'f'          )
    meta_keys = ( 'step', 't',  'dt' )
    
    results = Interpolated_Time_Series ()
    results .load ( outputfile, names, formats, meta_keys )
    
    # interpolate time dependent results using linear interpolation
    # this is needed since number of time steps and time step sizes
    # are usually different for every deterministic simulation
    results .interpolate ( 't', self.points + 1 )
    
    # compute meta parameters for interpolation 
    results.meta ['dt_i'] = numpy.diff (results.meta['t_i'])
    
    return results

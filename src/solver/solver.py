
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base Solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import sys
import subprocess
import shutil

import local

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
    if self.data == {}:
      self.zeros (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] += a.data [key] [step]
    return self
  
  def __isub__ (self, a):
    if self.data == {}:
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

class Solver (object):
  
  # common setup routines
  def setup (self):
    
    # copy executable to present working directory
    if local.cluster and self.path:
      shutil.copy (self.path + self.executable, '.')
  
  # check if nothing will be overwritten
  def check (self, level, type, sample, id):
    directory = self.directory (level, type, sample, id)
    if os.path.exists (directory):
      print
      print ' :: ERROR: working directory is NOT clean!'
      print '  : -> Remove all directories like "%s".' % directory
      print '  : -> Alternatively, run PyMLMC with \'-f\' option to force override.' 
      print
      sys.exit()
  
  # set default path from the environment variable
  def env (self, var):
    try:
      return os.environ [var] + '/'
    except:
      print
      print ' :: WARNING: environment variable %s not set.' % var
      print '  : -> Using path = None'
      print
      return None
  
  # return the name of a particular run
  def name (self, level, type, sample, id):
    return 'level=%d_type=%d_sample=%d_id=%d' % ( level, type, sample, id )
  
  # return the directory for a particular run
  def directory (self, level, type, sample, id):
    return self.name ( level, type, sample, id )
  
  # return the label (i.e. short name) of a particular run
  def label (self, prefix, level, type, sample):
    return '%s_%d_%d_%d' % (prefix, level, type, sample)
  
  # assemble args
  def args (self, parallelization):
    
    # initialize dictionary
    args = {}
    
    # additional options
    args ['options'] = self.options
    
    # number of threads must not exceed the specified number of cores
    args ['threads'] = min ( local.threads, parallelization.cores )
    
    # if cluster
    if local.cluster:
      
      # compute number of ranks
      args ['ranks'] = max ( 1, parallelization.cores / local.threads )
    
    return args
  
  # assemble the command
  def assemble (self, paralellization, args):
    
    # cluster run
    if local.cluster:
      
      # assemble excutable command
      args ['cmd'] = ('../' + self.cmd) % args
      
      # assemble job
      submit_args = {}
      if args ['ranks'] > 1:
        submit_args ['job']               = local.mpi_job % args
      else:
        submit_args ['job']               = local.job % args
      
      # assemble arguments for job submission
      submit_args ['ranks']   = args ['ranks']
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

    return cmd
  
  # execute the command
  def execute (self, cmd, directory, params):
    
    # create directory
    if directory != '.' and not os.path.exists (directory):
      os.mkdir ( directory )
    
    # copy needed input files
    if directory != '.':
      for inputfile in self.inputfiles:
        shutil.copy ( inputfile, directory + '/' )
    
    # report full submission command
    if params.verbose >= 1:
      print
      print cmd
      print
    
    # set stdout based on verbosity level
    if params.verbose >= 2:
      stdout = None
    else:
      stdout = open ( os.devnull, 'w' )
    
    # execute command
    if not params.simulate:
      subprocess.check_call ( cmd, cwd=directory, stdout=stdout, stderr=subprocess.STDOUT, shell=True, env=os.environ.copy() )


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

class Solver (object):
  
  scriptname = 'batch_%s'
  scriptfile = None
  sharedmem  = 0
  
  # common setup routines
  def setup (self, params):
    
    self.params = params
    
    # copy executable to present working directory
    if local.cluster and self.path:
      shutil.copy (self.path + self.executable, '.')
  
  # check if nothing will be overwritten
  def check (self, level, type, sample):
    directory = self.directory (level, type, sample)
    if not self.params.deterministic and os.path.exists (directory):
      print
      print ' :: ERROR: working directory is NOT clean!'
      print '  : -> Remove all directories like "%s".' % directory
      print '  : -> Alternatively, run PyMLMC with \'-f\' option to force override.' 
      print
      sys.exit()
  
  # init solver
  # TODO: 'init' shadows the constructor argument 'init' for script
  def begin (self, level, type, parallelization):
    
    # if batch mode -> init script
    if local.cluster and self.params.batch:
      self.scriptfile = open ( self.scriptname % self.directory (level, type), 'w' )
  
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
  
  # return the directory for a particular run
  def directory (self, level, type, sample=None):
    if self.params.deterministic:
      return '.'
    name = '%d_%d' % ( level, type )
    if sample != None:
      name += '_%d' % sample
    return name
  
  # return the label (= name_directory) of a particular run
  def label (self, directory):
    if self.params.deterministic:
      return self.name
    else:
      return '%s_%s' % (self.name, directory)
  
  # assemble args
  def args (self, parallelization):
    
    # initialize dictionary
    args = {}
    
    # additional options
    args ['options'] = self.options
    
    # number of threads
    args ['threads'] = parallelization.threads
    
    # number of ranks
    args ['ranks'] = parallelization.ranks
    
    return args
  
  # assemble job command
  def job (self, args):
    
    # if specified, execute the initialization function
    if self.init:
      self.init ( args ['seed'] )
    
    # cluster run
    if local.cluster:
      
      # assemble excutable command
      if self.params.deterministic:
        args ['cmd'] = ( './' + self.cmd) % args
      else:
        args ['cmd'] = ('../' + self.cmd) % args
    
    # node run
    else:
      
      # assemble executable command
      args ['cmd'] = self.cmd % args
    
    # assemble job
    # TODO: in fact, 'and not local.cluster' is _not_ needed -
    # the only problem is with _different_ binaries 'mpcf-node' and 'mpcf-cluster'
    if args ['ranks'] == 1 and not local.cluster:
      return local.simple_job % args
    else:
      return local.mpi_job % args
  
  # assemble the submission command
  def submit (self, job, parallelization, label):
    
    # assemble arguments for job submission
    args             = {}
    args ['job']     = job
    args ['ranks']   = parallelization.ranks
    args ['threads'] = parallelization.threads
    args ['cores']   = parallelization.cores
    args ['hours']   = parallelization.hours
    args ['minutes'] = parallelization.minutes
    args ['memory']  = parallelization.memory
    args ['label']   = label
    
    # assemble submission command
    return local.submit % args
  
  # launch a job - be it run immediately, submitted as is, or combined into a single script
  def launch (self, job, parallelization, directory):
    
    # prepare solver
    self.prepare (directory)
    
    # cluster run 
    if local.cluster:
      
      # if batch mode -> add job to script
      if self.params.batch:
        self.add ( job, directory )
      
      # else submit job to job management system
      else:
        self.execute ( self.submit (job, parallelization, self.label(directory)), directory )
    
    # node run -> execute job directly
    else:
      self.execute ( job )
  
  # prepare solver - create directories, copy files
  def prepare (self, directory):
    
    # create directory
    if not self.params.deterministic and not os.path.exists (directory):
      os.mkdir ( directory )
    
    # copy needed input files
    if not self.params.deterministic:
      for inputfile in self.inputfiles:
        shutil.copy ( inputfile, directory + '/' )
  
  # execute the command
  def execute (self, cmd, directory=None):
    
    # report full submission command
    if self.params.verbose >= 1:
      print
      print cmd
      print
    
    # set stdout based on verbosity level
    if self.params.verbose >= 2:
      stdout = None
    else:
      stdout = open ( os.devnull, 'w' )
    
    # execute command
    if not self.params.simulate:
      subprocess.check_call ( cmd, cwd=directory, stdout=stdout, stderr=subprocess.STDOUT, shell=True, env=os.environ.copy() )
  
  # add command to script
  def add (self, cmd, directory):
    
    # add cmd to the script
    self.scriptfile.write ( '\n' )
    if not self.params.deterministic:
      self.scriptfile.write ( 'cd %s\n' % directory )
    self.scriptfile.write ( cmd + '\n' )
    if not self.params.deterministic:
      self.scriptfile.write ( 'cd ..\n' )
  
  # execute the script
  def exit (self, level, type, parallelization):
    
    # if batch mode -> submit script
    if local.cluster and self.params.batch:
      
      # close script file
      self.scriptfile.close()
      
      # assemble batch job for the generated script
      job = local.batch_job % { 'script' : self.scriptname % self.directory (level, type) }
      
      # submit script to job management system
      label = self.label ( self.directory (level, type) )
      self.execute ( self.submit (job, parallelization, label) )

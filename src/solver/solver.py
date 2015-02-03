
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
  
  jobfile    = 'job.sh'
  scriptfile = 'submit.sh'
  inputdir   = 'input'
  outputdir  = 'output'
  
  sharedmem  = 0
  
  batch         = ''
  bathfiles     = []
  
  # common setup routines
  def setup (self, params):
    
    self.params = params
    
    # prepare scratch
    if local.scratch:
      
      # assemble sub-directory
      runpath, rundir = os.path.split (os.getcwd())
      scratchdir = os.path.join (local.scratch, rundir)
      
      # prepare scratch directory
      if not os.path.exists (scratchdir):
        os.mkdir (scratchdir)
      
      # create symlink to scratch
      if not os.path.exists (self.outputdir):
        os.symlink (scratchdir, self.outputdir)
    
    # otherwise create output directory
    else:
      if not os.path.exists (self.outputdir):
        os.mkdir (self.outputdir)
    
    # copy executable to output directory
    if local.cluster and self.path:
      shutil.copy ( os.path.join (self.path, self.executable), self.outputdir)
  
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
  
  # initialize solver
  def initialize (self, level, type, parallelization):
    if parallelization.batch:
      self.batch = ''
      self.batchfiles = []
  
  # set default path from the environment variable
  def env (self, var):
    try:
      return os.environ [var]
    except:
      print
      print ' :: WARNING: environment variable %s not set.' % var
      print '  : -> Using path = None'
      print
      return None
  
  # return the directory for a particular run
  def directory (self, level, type, sample=None):
    
    if self.params.deterministic:
      return self.outputdir
    
    else:
      dir = '%d_%d' % (level, type)
      if sample != None:
        dir += '/%d' % sample
      return os.path.join ( self.outputdir, dir )
  
  # return the label of a particular run
  def label (self, level, type, sample=None):
    
    if self.params.deterministic:
      return self.name
    
    else:
      dir = '%d_%d' % (level, type)
      if sample != None:
        dir += '_%d' % sample
      return '%s_%s' % (self.name, dir)
  
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
    
    # number of cores
    args ['cores'] = parallelization.cores
    
    # number of nodes
    args ['nodes'] = parallelization.nodes
    
    # number of tasks
    args ['tasks'] = parallelization.tasks
    
    # custom environment variables
    args ['envs'] = local.envs
    
    return args
  
  # assemble job command
  def job (self, args):
    
    # if input directory does not exist, create it
    if not os.path.exists (self.inputdir):
      os.mkdir (self.inputdir)
    
    # if specified, execute the initialization function
    if self.init:
      self.init ( args ['seed'] )
    
    # cluster run
    if local.cluster:
      
      # assemble excutable command
      if self.params.deterministic:
        args ['cmd'] = os.path.join ('.',  self.cmd) % args
      else:
        args ['cmd'] = os.path.join (os.path.join ('..','..'), self.cmd) % args
    
    # node run
    else:
      
      # assemble executable command
      args ['cmd'] = self.cmd % args
    
    # assemble job
    # TODO: in fact, 'and not local.cluster' is _not_ needed -
    # the only problem is with _different_ binaries 'mpcf-node' and 'mpcf-cluster'
    # also, 'export OMP_NUM_THREADS=%(threads)d;' in front of binary does not work with LSF, for instance
    if args ['ranks'] == 1 and not local.cluster:
      return local.simple_job % args
    else:
      return local.mpi_job % args
  
  # assemble the submission command
  def submit (self, job, parallelization, label, directory='.'):
    
    # add timer
    if local.timer:
      job = '%s (%s)' % (local.timer, job)
    
    # create jobfile
    with open ( os.path.join (directory, self.jobfile), 'w') as f:
      f.write ('#!/bin/bash\n\n')
      f.write (job)
    
    # assemble arguments for job submission
    args              = {}
    args ['job']      = job
    args ['jobfile']  = self.jobfile
    args ['ranks']    = parallelization.ranks
    args ['threads']  = parallelization.threads
    args ['cores']    = parallelization.cores
    args ['nodes']    = parallelization.nodes
    args ['tasks']    = parallelization.tasks
    args ['hours']    = parallelization.hours
    args ['minutes']  = parallelization.minutes
    args ['memory']   = parallelization.memory
    args ['label']    = label
    args ['xopts']    = self.params.xopts
    
    # assemble submission script (if enabled)
    if local.script:
      args ['script']     = local.script % args
      args ['scriptfile'] = self.scriptfile
      with open (os.path.join (directory, self.scriptfile), 'w') as f:
        f.write ( args ['script'] )
      if self.params.verbose >= 1:
        print
        print '=== SCRIPT ==='
        print args ['script']
        print '==='
    
    # assemble submission command
    return local.submit % args
  
  # launch a job from the specified 'args' and 'parallelization'
  # depending on parameters, job will be run immediately or will be submitted to a queueing system
  # for parallelization.batch = 1, all jobs (for specified level and type) are combined into a single script
  def launch (self, args, parallelization, level, type, sample):
    
    # assemble job
    job = self.job (args)
    
    # get directory
    directory = self.directory (level, type, sample)
    
    # prepare solver
    self.prepare (directory)
    
    # cluster run 
    if local.cluster:
      
      # if batch mode -> add job to batch script
      # all jobs are combined into a single script
      if parallelization.batch:
        self.add ( job, sample )
      
      # else submit job to job management system
      else:
        label = self.label (level, type, sample)
        self.execute ( self.submit (job, parallelization, label, directory), directory )
    
    # node run -> execute job directly
    else:
      self.execute ( job )
  
  # prepare solver - create directories, copy files
  def prepare (self, directory):
    
    # create directory
    if not self.params.deterministic and not os.path.exists (directory):
      os.makedirs ( directory )
    
    # copy needed input files
    if os.path.exists (self.inputdir):
      for inputfile in os.listdir (self.inputdir):
        shutil.copy ( os.path.join (self.inputdir, inputfile), directory )
  
  # execute the command
  def execute (self, cmd, directory='.'):
    
    # report command
    if self.params.verbose >= 1:
      print
      print '=== EXECUTE ==='
      print 'DIR: ' + directory
      print 'CMD: ' + cmd
      print '==='
      print
    
    # set stdout based on verbosity level
    if self.params.verbose >= 2:
      stdout = subprocess.STDOUT
    else:
      stdout = open ( os.devnull, 'w' )
    
    # execute command
    if not self.params.simulate:
      subprocess.check_call ( cmd, cwd=directory, stdout=stdout, stderr=subprocess.STDERR, shell=True, env=os.environ.copy() )
  
  # add cmd to script
  def add (self, job, sample):
    
    # add cmd to the script
    text = '\n'
    text += 'cd %s\n' % sample
    text += job + '\n'
    text += 'cd ..\n'
    
    # add cmd to the batch script
    self.batch += text
    
    # report command
    if self.params.verbose >= 1:
      print text
  
  # finalize solver
  def finalize (self, level, type, parallelization):
    
    # if batch mode -> submit batch job
    if local.cluster and parallelization.batch:
      
      # get directory
      directory = self.directory (level, type)
      
      # submit
      label = self.label (level, type)
      self.execute ( self.submit (self.batch, parallelization, label, directory), directory )

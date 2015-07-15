
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
import stat

import local

class Solver (object):
  
  jobfile    = 'job_%s.sh'
  scriptfile = 'script_%s.sh'
  submitfile = 'submit_%s.sh'
  statusfile = 'status_%s.dat'
  timerfile  = 'timerfile_%s.dat'
  inputdir   = 'input'
  outputdir  = 'output'
  
  # common setup routines
  def setup (self, params, root, deterministic):
    
    self.params        = params
    self.root          = root
    self.deterministic = deterministic
    
    # create output directory
    if not os.path.exists (self.outputdir):
    
      # prepare scratch
      if local.scratch:
      
        # assemble sub-directory
        runpath, rundir = os.path.split (os.getcwd())
        scratchdir = os.path.join (local.scratch, rundir)
        
        # prepare scratch directory
        if not os.path.exists (scratchdir):
          os.mkdir (scratchdir)
        
        # create symlink to scratch
        os.symlink (scratchdir, self.outputdir)
      
      # otherwise create output directory
      else:
        os.mkdir (self.outputdir)
    
    # copy executable to output directory
    if local.cluster and self.path:
      if not os.path.exists ( os.path.join (self.outputdir, self.executable) ):
        executablepath = os.path.join (self.path, self.executable)
        if os.path.exists ( executablepath ):
          shutil.copy ( executablepath, self.outputdir)
        else:
          print
          print ' :: ERROR: executable not found at ' + executablepath
          print
          sys.exit()
  
  # check if nothing will be overwritten
  def check (self, level, type, sample):
    directory = self.directory (level, type, sample)
    if not self.deterministic:
      present = os.path.exists (directory)
    else:
      label = self.label (level, type, sample)
      present = os.path.exists ( os.path.join (directory, self.jobfile % label) )
    if present:
      print
      print ' :: ERROR: working directory is NOT clean!'
      print '  : -> Remove all directories like "%s".' % directory
      print '  : -> Alternatively, run PyMLMC with \'-p\' option to proceed with simulations.'
      print
      sys.exit()
  
  # initialize solver
  def initialize (self, level, type, parallelization):
    if parallelization.batch:
      self.batch = []
  
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

  # make file executable
  def chmodx (self, filename):
    os.chmod (filename, os.stat (filename) .st_mode | stat.S_IEXEC)

  # return the directory for a particular run
  def directory (self, level, type, sample=None):
    
    if self.deterministic:
      return os.path.join (self.root, self.outputdir)
    
    else:
      dir = '%d_%d' % (level, type)
      if sample != None:
        dir += '/%d' % sample
      return os.path.join (os.path.join (self.root, self.outputdir), dir)
  
  # return the label of a particular run
  def label (self, level, type, sample=None):
    
    if self.deterministic:
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
    
    # number of cores per node
    args ['cpucores'] = parallelization.cpucores
    
    # email for notification
    args ['email'] = parallelization.email
    
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
      if self.deterministic:
        args ['cmd'] = os.path.join ('.',  self.cmd) % args
      else:
        args ['cmd'] = os.path.join (os.path.join ('..','..'), self.cmd) % args
    
    # node run
    else:
      
      # assemble executable command
      args ['cmd'] = self.cmd % args
    
    # assemble job
    if args ['ranks'] == 1 and not local.cluster:
      return local.simple_job % args
    else:
      return local.mpi_job % args
  
  # assemble the submission command
  def submit (self, job, parallelization, label, directory='.'):
    
    # check if walltime does not exceed 'local.max_walltime'
    if parallelization.walltime > local.max_walltime:
      print ' :: ERROR: \'walltime\' exceeds \'max_walltime\' in \'local.py\': %.2f > %.2f' % (parallelization.walltime, local.max_walltime)
      sys.exit()
    
    # add timer
    if local.timer:
      job = local.timer % { 'job' : job, 'timerfile' : self.timerfile % label, 'statusfile' : self.statusfile % label }
    
    # create jobfile
    jobfile = os.path.join (directory, self.jobfile % label)
    with open ( jobfile, 'w') as f:
      f.write ('#!/bin/bash\n')
      f.write (job)
      self.chmodx (jobfile)
    
    # assemble arguments for job submission
    args              = {}
    args ['job']      = job
    args ['jobfile']  = self.jobfile % label
    args ['ranks']    = parallelization.ranks
    args ['threads']  = parallelization.threads
    args ['cores']    = parallelization.cores
    args ['nodes']    = parallelization.nodes
    args ['tasks']    = parallelization.tasks
    args ['hours']    = parallelization.hours
    args ['minutes']  = parallelization.minutes
    args ['memory']   = parallelization.memory
    args ['cpucores'] = parallelization.cpucores
    args ['label']    = label
    args ['email']    = parallelization.email
    args ['xopts']    = self.params.xopts
    
    # take bootup time into account
    if args ['hours'] == 0 and args ['minutes'] < 2 * local.bootup:
      args ['minutes'] += local.bootup

    # assemble submission script (if enabled)
    if local.script:
      args ['script']     = local.script % args
      args ['scriptfile'] = self.scriptfile % label
      scriptfile = os.path.join (directory, self.scriptfile % label)
      with open (scriptfile, 'w') as f:
        f.write ( args ['script'] )
        self.chmodx (scriptfile)
      if self.params.verbose >= 1:
        print
        print '=== SCRIPT ==='
        print args ['script']
        print '==='
  
    # create submit script
    submitfile = os.path.join (directory, self.submitfile % label)
    with open (submitfile, 'w') as f:
      f.write ( local.submit % args )
      self.chmodx (submitfile)
    
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
    
    # get label
    label = self.label (level, type, sample)
    
    # append command to create status file
    job += '\n' + 'touch %s' % ( self.statusfile % label )
    
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
        self.execute ( self.submit (job, parallelization, label, directory), directory )
    
    # node run -> execute job directly
    else:
      self.execute ( job )
  
  # prepare solver - create directories, copy files
  def prepare (self, directory):
    
    # create directory
    if not self.deterministic and not os.path.exists (directory):
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
    
    # set stdout and stderr based on verbosity level
    if self.params.verbose >= 2:
      stdout = None
      stderr = None
    else:
      stdout = open ( os.devnull, 'w' )
      stderr = subprocess.STDOUT
    
    # execute command
    if not self.params.simulate:
      subprocess.check_call ( cmd, cwd=directory, stdout=stdout, stderr=stderr, shell=True, env=os.environ.copy() )
  
  # add job to batch
  def add (self, job, sample):
    
    # add cmd to the script
    cmd = '\n'
    cmd += 'cd %s\n' % sample
    cmd += job + '\n'
    cmd += 'cd ..\n'
    
    # add cmd to the batch
    self.batch.append (cmd)
    
    # report command
    if self.params.verbose >= 1:
      print cmd
  
  # finalize solver
  def finalize (self, level, type, parallelization):
    
    # if batch mode -> submit batch job(s)
    if local.cluster and parallelization.batch:
      
      # get directory
      directory = self.directory (level, type)
      
      # split batch job into parts
      parts = [ self.batch [i:i+parallelization.batchsize] for i in range (0, len(self.batch), parallelization.batchsize) ]
      
      # submit each part of the batch job
      for i, part in enumerate(parts):
        
        # extract required part of the batch job
        batch = ''.join (part)
        
        # submit
        label = self.label (level, type) + '_b%d' % (i+1)
        self.execute ( self.submit (batch, parallelization, label, directory), directory )
  
  # check if the job is finished
  # (required only for non-interactive sessions)
  def finished (self, level, type, sample):
    
    # get directory
    directory = self.directory ( level, type, sample )

    # get label
    label = self.label ( level, type, sample )

    # check if the status file exists
    return os.path.exists ( os.path.join (directory, self.statusfile % label) )

  # report timer results
  def timer (self, level, type, sample, batch):
    
    if batch [level] [type]:
      
      # get directory
      directory = self.directory ( level, type )
      
      # get label
      label = self.label ( level, type ) + '_b1'
    
    else:
      
      # get directory
      directory = self.directory ( level, type, sample )
      
      # get label
      label = self.label ( level, type, sample )
    
    # read timer file
    timerfilepath = os.path.join (directory, self.timerfile % label)
    if os.path.exists (timerfilepath):
      with open ( timerfilepath, 'r' ) as f:
        lines = f.readlines()
        if len (lines) >= 3:
          line = lines [-3]
          time = line.strip().split(' ') [-1]
        else:
          time = None
    else:
      time = None
    
    try:
      return float (time)
    except:
      return None

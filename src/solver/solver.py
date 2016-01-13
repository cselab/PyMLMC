
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
import math

import local
import helpers

class Solver (object):
  
  jobfile    = 'job_%s.sh'
  scriptfile = 'script_%s.sh'
  submitfile = 'submit_%s.sh'
  statusfile = 'status_%s.dat'
  timerfile  = 'timerfile_%s.dat'
  inputdir   = 'input'
  outputdir  = 'output'
  path       = None
  init       = None
  
  # common setup routines
  def setup (self, params, root, deterministic):
    
    self.params        = params
    self.root          = root
    self.deterministic = deterministic

    # setup name
    if not hasattr (self, 'name'):
      self.name = self.__class__.__name__
    
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

      # for proceeding simulations, reusing of an old executable might be prefered
      reuse = 0
      if self.params.proceed and os.path.exists ( os.path.join (self.outputdir, self.executable) ):
        reuse = helpers.query ('Old executable present. Reuse?', exit=0)
      if reuse != 'y':
        executablepath = os.path.join (self.path, self.executable)
        if os.path.exists ( executablepath ):
          shutil.copy ( executablepath, self.outputdir)
        else:
          helpers.error ('executable not found at ' + executablepath)
  
  # check if nothing will be overwritten
  def check (self, level, type, sample):
    directory = self.directory (level, type, sample)
    if not self.deterministic:
      present = os.path.exists (directory)
    else:
      label = self.label (level, type, sample)
      present = os.path.exists ( os.path.join (directory, self.jobfile % label) )
    if present:
      message = 'working directory is NOT clean!'
      details = 'Remove all directories like "%s"' % directory
      advice  = 'Alternatively, run PyMLMC with \'-o\' option to override or with \'-p\' option to proceed with simulations'
      helpers.error (message, details, advice)

  # initialize solver
  def initialize (self, level, type, parallelization, iteration):
    if parallelization.batch:
      self.batch = []
    self.iteration = iteration
  
  # set default path from the environment variable
  def env (self, var):
    try:
      return os.environ [var]
    except:
      helpers.warning ('environment variable %s not set' % var, details = 'Using path = None')
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
      #dir = '%d%s' % (level, ['f', 'c'] [type])
      if sample != None:
        dir += '/%d' % sample
      return os.path.join (os.path.join (self.root, self.outputdir), dir)
  
  # return the label of a particular run
  def label (self, level, type, sample=None, suffix='', iteration=True):
    
    if self.deterministic:
      return self.name + suffix + ('.%d' % self.iteration if iteration else '')
    
    else:
      dir = '%d_%d' % (level, type)
      #dir = '%d%s' % (level, ['f', 'c'] [type])
      if sample != None:
        dir += '_%d' % sample
      return '%s_%s%s' % (self.name, dir, suffix) + ('.%d' % self.iteration if iteration else '')
  
  # assemble job command
  def job (self, args):
    
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
  def submit (self, job, parallelization, label, directory='.', timer=0):
    
    # check if walltime does not exceed 'local.max_walltime'
    if parallelization.walltime > local.max_walltime (parallelization.cores):
      helpers.error ('\'walltime\' exceeds \'max_walltime\' in \'local.py\'', details = '%.2f > %.2f' % (parallelization.walltime, local.max_walltime))
    
    # add timer
    if timer and local.timer:
      job = local.timer % { 'job' : '\n' + job, 'timerfile' : self.timerfile % label }
    
    # create jobfile
    jobfile = os.path.join (directory, self.jobfile % label)
    with open ( jobfile, 'w') as f:
      f.write ('#!/bin/bash\n')
      f.write (job)
      self.chmodx (jobfile)
    
    # assemble arguments for job submission
    args              = parallelization.args()
    args ['job']      = job
    args ['jobfile']  = self.jobfile % label
    args ['label']    = label
    args ['xopts']    = self.params.xopts

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

    # adjust parallelization to take into account 'batch' and 'merge' modes
    # TODO: maybe would be better to introduce separate variables, such as 'walltime_batch', 'nodes_merge', etc.
    args.update ( parallelization.adjust().args() )

    # assemble submission command
    submit = local.submit % args

    # create submit script
    submitfile = os.path.join (directory, self.submitfile % label)
    with open (submitfile, 'w') as f:
      f.write (submit)
      self.chmodx (submitfile)

    # return submission command
    return submit
  
  # launch a job from the specified 'args' and 'parallelization'
  # depending on parameters, job will be run immediately or will be submitted to a queueing system
  # for parallelization.batch = 1, all jobs (for specified level and type) are combined into several batch scripts
  def launch (self, args, parallelization, level, type, sample):

    # append options to args
    args ['options'] = self.options

    # assemble job
    job = self.job (args)
    
    # get directory
    directory = self.directory (level, type, sample)
    
    # get label
    label = self.label (level, type, sample)

    # prepend command to print date
    job = 'date\n' + job

    # append command to create status file
    job = job.rstrip() + '\n' + 'touch %s' % ( self.statusfile % self.label (level, type, sample, iteration=None) )

    # add timer
    if local.timer:
      job = local.timer % { 'job' : '\n' + job + '\n', 'timerfile' : self.timerfile % label }

    # prepare solver
    if not self.params.proceed:
      self.prepare (directory, args ['seed'])
    
    # cluster run 
    if local.cluster:
      
      # if batch mode -> add job to batch script
      # all jobs are combined into a single script
      if parallelization.batch:
        self.add ( job, sample )
      
      # else submit job to job management system
      else:

        # else set block hook
        job = job.replace ('BATCH_JOB_BLOCK_HOOK', local.BATCH_JOB_BLOCK_HOOK) % {'batch_id' : 0}

        # submit
        self.execute ( self.submit (job, parallelization, label, directory), directory )
    
    # node run -> execute job directly
    else:
      self.execute ( job )
  
  # prepare solver - create directories, copy files, execute init script
  def prepare (self, directory, seed):
    
    # create directory
    if not self.deterministic and not os.path.exists (directory):
      os.makedirs ( directory )

    # copy needed input files
    if os.path.exists (self.inputdir):
      for inputfile in os.listdir (self.inputdir):
        shutil.copy ( os.path.join (self.inputdir, inputfile), directory )

    # if specified, execute solver init script
    if self.init and not self.params.noinit:
      self.init ( directory, seed )
  
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
    cmd  = 'cd %s\n' % sample
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
      
      # split batch jobs into parts
      if parallelization.batchmax:
        parts = [ self.batch [i:i+parallelization.batchmax] for i in range (0, len (self.batch), parallelization.batchmax) ]
      else:
        parts = [ self.batch [:] ]

      # if merging into ensembles is disabled
      if not local.ensembles:

        # submit each part of the batch job
        for i, part in enumerate (parts):

          # construct batch job
          batch = '\n'.join (part)

          # set batch in parallelization
          parallelization.batch = len (part)

          # set label
          label = self.label (level, type, suffix='_b%d' % (i+1))

          # submit
          self.execute ( self.submit (batch, parallelization, label, directory, timer=1), directory )

      # else if merging into ensembles is enabled
      else:

        # split parts into ensembles (with size being powers of 2)
        binary = bin ( len(parts) )
        decomposition = [ 2**(len(binary) - 1 - power) if flag == '1' else 0 for power, flag in enumerate(binary) ]
        decomposition = [ size for size in decomposition if size != 0 ]

        # respect parallelization.mergemax
        filtered = []
        for i, size in enumerate (decomposition):
          if parallelization.mergemax == None or size <= parallelization.mergemax:
            filtered += [size]
          else:
            chunks = 2 ** int ( math.ceil ( math.log ( float(size) / parallelization.mergemax, 2) ) )
            filtered += [ size / chunks ] * chunks
        decomposition = filtered

        # submit each ensemble
        submitted   = 0
        batch_index = 0
        for i, size in enumerate (decomposition):

          # set label
          label = self.label (level, type, suffix='_e%d' % (i+1))
          
          # initialize ensemble job
          ensemble = ''

          # prepare each part of the batch job
          for batch_index_local, part in enumerate (parts [submitted : submitted + size]):

            # prepare job to be part of an ensemble with batch job id = i
            # TODO: replace this by proper formatting, i.e. in job: %(batch_id_hook)s, set from local.cfg and using %(batch_id)d, and then set batch_id here
            part = [ job.replace ('BATCH_JOB_BLOCK_HOOK', local.BATCH_JOB_BLOCK_HOOK) % {'batch_id' : batch_index_local} for job in part ]

            # construct batch job
            batch = '\n'.join (part)

            # increment 'batch_index' counter
            batch_index += 1

            # add timer
            if local.timer:
              label_timer = self.label (level, type, suffix='_b%d' % batch_index)
              batch = local.timer % { 'job' : '\n\n' + batch + '\n', 'timerfile' : self.timerfile % label_timer }

            # fork to background (such that other batch jobs in ensemble could proceed)
            batch = '(\n\n%s\n\n) &\n' % batch

            # header for the ensemble job
            ensemble += '\n# === BATCH JOB %d [local index %d]\n' % (batch_index, batch_index_local)
            
            # add batch job to the ensemble
            ensemble += batch

          # set batch and merge in parallelization
          parallelization.batch = len (part)
          parallelization.merge = size

          # submit
          self.execute ( self.submit (ensemble, parallelization, label, directory), directory )

          # update 'submitted' counter
          submitted += size

        # return information about ensembles
        from helpers import intf
        # TODO: this is not very clean: 'parallelization.nodes * size'
        info = [ '%s (%s N)' % ( intf (size), intf (parallelization.nodes * size) ) for size in decomposition ]
        return ' + '.join (info)

  # check if the job is finished
  # (required only for non-interactive sessions)
  def finished (self, level, type, sample):
    
    # get directory
    directory = self.directory ( level, type, sample )

    # get label
    label = self.label ( level, type, sample, iteration=None )

    # check if the status file exists
    return os.path.exists ( os.path.join (directory, self.statusfile % label) )

  # report timer results
  # TODO: if merge or batch, sample should map to correct '_b*' or '_e*'
  # ALTERNATIVE: already in mc.timer(), load all using glob(*_b*.iteration) + glob(*_e*.iteration)
  # REMARK: 'glob(*_e*.iteration)' is required for legacy simulations
  def timer (self, level, type, batch, sample=None):

    if merge [level] [type]:

      # get directory
      directory = self.directory ( level, type )

      # get label
      label = self.label ( level, type, suffix = '_e1' )

    elif batch [level] [type]:
      
      # get directory
      directory = self.directory ( level, type )
      
      # get label
      label = self.label ( level, type, suffix = '_b1' )

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

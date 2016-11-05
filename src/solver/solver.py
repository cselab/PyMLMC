
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
import copy

import local
import helpers

class Solver (object):
  
  jobfile    = 'job.sh'
  scriptfile = 'script.sh'
  submitfile = 'submit.sh'
  statusfile = 'status.dat'
  timerfile  = 'timerfile.dat'
  reportfile = 'report.dat'
  inputdir   = 'input'
  outputdir  = 'output'
  path       = None
  init       = None
  workunit   = 1
  batch      = []

  # common setup routines
  def setup (self, scheduler, params, root, deterministic, recycle):
    
    # save configuration
    vars (self) .update ( locals() )

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
          helpers.error ('executable not found!', details='at ' + executablepath, advice='Make sure executable exists or modify \'solver.executable\' value.')
  
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
      helpers.warning ('environment variable %s not set' % var, details = 'Using: path = None')
      return None

  # make file executable
  def chmodx (self, filename):
    os.chmod (filename, os.stat (filename) .st_mode | stat.S_IEXEC)

  # return the directory for a particular run
  def directory (self, level, type, sample=None):
    
    if self.deterministic:
      return os.path.join (self.root, self.outputdir)
    
    else:
      if self.recycle:
        #dir = '%d%s' % (level, ['f', 'c'] [type])
        dir = '%d' % level
      else:
        #dir = '%d_%d' % (level, type)
        dir = '%d%s' % (level, ['f', 'c'] [type])
      if sample != None:
        dir += '/%d' % sample
      return os.path.join (os.path.join (self.root, self.outputdir), dir)
  
  # return the label of a particular run
  def label (self, level, type, sample=None, suffix='', iteration=True):
    
    if self.deterministic:
      return self.name + suffix
    
    else:
      if self.recycle:
        dir = '%d' % level
      else:
        #dir = '%d_%d' % (level, type)
        dir = '%d%s' % (level, ['f', 'c'] [type])
      if sample != None:
        dir += '_%d' % sample
      return '%s_%s%s' % (self.name, dir, suffix) + ('.%d' % self.iteration if iteration else '')
  
  # assemble job command
  def job (self, args, block=0, corner=0, shape=None, wrap=True):
    
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

    # if no wrapping is required
    if not wrap:

      # return plain execution command only
      return args ['cmd']

    # set default harware topology arguments
    args ['block']  = block
    args ['corner'] = corner
    args ['shape']  = shape

    # TODO: this is a dirty fix
    if local.ensembles:
      if local.block != None:
        args ['envs'] += ' ' + local.block % args
      if shape != None:
        args ['envs'] += ' ' + local.corner % args
        args ['envs'] += ' ' + local.shape % args

    # assemble job
    if args ['ranks'] == 1 and not local.cluster:
      job = local.simple_job.rstrip() % args
    else:
      job = local.mpi_job.rstrip() % args

    # prepend command to print date
    job = 'date\n' + job

    # append command to create status file
    job = job.rstrip() + '\n' + 'touch %s' % self.statusfile

    # add timer
    if local.timer:
      job = local.timer.rstrip() % { 'job' : '\n' + job + '\n', 'timerfile' : self.timerfile }

    return job
  
  # assemble the submission command
  def submit (self, job, parallelization, label, directory='.', timer=0, suffix='', boot=1):
    
    # check if walltime does not exceed 'local.max_walltime'
    if parallelization.walltime > local.max_walltime (parallelization.cores):
      helpers.error ('\'walltime\' exceeds \'max_walltime\' in \'local.py\'', details = '%.2f > %.2f' % (parallelization.walltime, local.max_walltime))

    # add booting and freeing
    if boot and local.boot:
      job = self.boot (job)

    # add timer
    if timer and local.timer:
      job = local.timer.rstrip() % { 'job' : '\n' + job, 'timerfile' : self.timerfile + suffix }
    
    # create jobfile
    jobfile = os.path.join (directory, self.jobfile + suffix)
    with open ( jobfile, 'w' ) as f:
      f.write ('#!/bin/bash\n')
      f.write (job)
      self.chmodx (jobfile)
    
    # assemble arguments for job submission
    args                = parallelization.args()
    args ['job']        = job
    args ['jobfile']    = self.jobfile + suffix
    args ['reportfile'] = self.reportfile + suffix
    args ['label']      = label
    args ['xopts']      = self.params.xopts

    # create a copy of parallelization to avoid override
    parallelization = copy.deepcopy (parallelization)

    # update args with adjusted parallelization
    # TODO: maybe would be better to introduce separate variables, such as 'walltime_batch', 'nodes_merge', etc.
    args.update ( parallelization.adjust().validate().args() )

    # assemble submission script (if enabled)
    if local.script:
      args ['script']     = local.script.rstrip() % args
      args ['scriptfile'] = self.scriptfile + suffix
      scriptfile = os.path.join (directory, self.scriptfile + suffix)
      with open (scriptfile, 'w') as f:
        f.write ( args ['script'] )
        self.chmodx (scriptfile)
      if self.params.verbose >= 1:
        print
        print '=== SCRIPT ==='
        print args ['script']
        print '==='

    # assemble submission command
    submit = local.submit % args

    # create submit script
    submitfile = os.path.join (directory, self.submitfile + suffix)
    with open (submitfile, 'w') as f:
      f.write (submit)
      self.chmodx (submitfile)

    # return submission command
    return submit
  
  # launch a job from the specified 'args' and 'parallelization'
  # depending on parameters, job will be run immediately or will be submitted to a queueing system
  # for parallelization.batch = 1, all jobs (for specified level and type) are combined into several batch scripts
  def launch (self, args, parallelization, level, type, sample):

    # append sample to args
    args ['sample'] = sample

    # get directory
    directory = self.directory (level, type, sample)

    # prepare solver
    if not self.params.proceed:
      self.prepare (directory, args ['seed'])
    
    # cluster run or specific dispatch routine
    if local.cluster or self.scheduler.dispatch != None:
      
      # if batch mode -> add job to batch
      if parallelization.batch:
        self.batch.append (args)
      
      # else submit job to job management system under specified label
      else:

        # get label
        label = self.label (level, type, sample)

        # submit
        self.execute (self.submit (self.job (args), parallelization, label, directory), directory)
    
    # node run -> execute job directly
    else:
      self.execute (self.job (args))
  
  # prepare solver - create directories, copy files, execute init script
  def prepare (self, directory, seed):
    
    # create directory
    if not self.deterministic and not os.path.exists (directory):
      os.makedirs (directory)

    # copy needed input files
    if os.path.exists (self.inputdir):
      for inputfile in os.listdir (self.inputdir):
        shutil.copy (os.path.join (self.inputdir, inputfile), directory)

    # if specified, execute solver init script
    if self.init and not self.params.noinit:
      self.init (directory, seed)
  
  # fork job to background
  def fork (self, job):
    return '(\n\n%s\n\n) &\n' % job

  # add synchronization
  def sync (self):
    return '\n' + 'wait'
  
  # add booting and freeing
  def boot (self, job, block=0):

    if local.boot and local.free:
      boot = local.boot % {'block' : block}
      free = local.free % {'block' : block}
      job = '%s\n\n%s\n\n%s\n' % (boot, job, free)
      return job

    else:
      return job

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
      stdout = subprocess.PIPE#open (os.devnull, 'w')
      stderr = subprocess.PIPE#subprocess.STDOUT
    
    # execute command
    if not self.params.simulate:
      process = subprocess.Popen (cmd, cwd=directory, stdout=stdout, stderr=stderr, shell=True, env=os.environ.copy())
      output  = process.communicate()
      failed  = process.poll()
      if failed:
        message = 'Submission failed'
        helpers.warning (message, details=str(process.stdout))
  
  # wrap job inside the batch
  def wrap (self, job, sample):

    # add directory changes
    wrapped = ('cd %s\n' % sample) + job + '\n' + 'cd ..\n'
    
    # report command
    if self.params.verbose >= 1:
      print wrapped

    return wrapped

  # dispatch all jobs
  def dispatch (self, level, type, parallelization):

    # get directory
    directory = self.directory (level, type)

    # copy parallelization for further modifications
    parallelization = copy.deepcopy (parallelization)

    # if available, use scheduler's dispatch routine
    if self.scheduler.dispatch != None:

      # set label
      label = self.label (level, type)

      jobs = [ self.job (args, wrap=False) for args in self.batch ]

      # dispatch and get info
      info = self.scheduler.dispatch (self.batch, jobs, directory, label, parallelization)

      # empty queue
      self.batch = []

      return info

    # if batch mode -> submit batch job(s)
    if local.cluster and parallelization.batch:

      # suffix format for batch jobs and ensembles
      suffix_format = '.%s%03d'

      # split batch job into smaller batches according to 'parallelization.batchmax'
      if parallelization.batchmax:
        batches = helpers.chunks (self.batch, parallelization.batchmax)
      else:
        batches = [ self.batch [:] ]

      # if merging into ensembles is disabled
      if not local.ensembles:

        # submit each batch
        for index, batch in enumerate (batches):

          # set batch in parallelization (last batch might be smaller)
          parallelization.batch = len (batch)

          # construct batch job from all jobs in the current batch
          batch = '\n'.join ( [ self.wrap (self.job (args), args ['sample']) for args in batch ] )

          # set suffix
          suffix = suffix_format % ('b', index + 1)

          # set label
          label = self.label (level, type, suffix=suffix)

          # submit
          self.execute ( self.submit (batch, parallelization, label, directory, suffix=suffix, timer=1), directory )

        # empty queue
        self.batch = []

        return ''

      # else if merging into ensembles is enabled
      else:

        # check if blocks need to be split into subblocks
        subblocks = max (1, local.min_cores / parallelization.cores)

        # form blocks each containing grouped 'subblocks' batch jobs
        blocks = helpers.chunks (batches, subblocks)

        # warn if the first block is not fully utilized
        if len (blocks) > 1:
          utilized = parallelization.cores * len (blocks [0]) >= local.min_cores
        '''
        if not utilized:
          message = 'Requested number of cores and samples does not fully utilize the smallest block'
          details = '%s * %s < %s' % ( helpers.intf (parallelization.cores), helpers.intf (len (blocks [0])), helpers.intf (local.min_cores) )
          advice  = 'Increase paralellization ratio for this level'
          helpers.warning (message, details=details, advice=advice)
          # TODO: in such case, should batchsize be reduced (for all under-utilized blocks) to improve the utilization?
        '''

        # split blocks into ensembles (with ensemble sizes being powers of 2)
        binary = bin ( len (blocks) )
        decomposition = [ 2**(len(binary) - 1 - power) if flag == '1' else 0 for power, flag in enumerate(binary) ]
        decomposition = [ size for size in decomposition if size != 0 ]

        # respect parallelization.mergemax
        filtered = []
        for i, size in enumerate (decomposition):
          if parallelization.mergemax == None or size * subblocks <= parallelization.mergemax:
            filtered += [size]
          else:
            chunks = 2 ** int ( math.ceil ( math.log ( float (size * subblocks) / parallelization.mergemax, 2) ) )
            filtered += [ size / chunks ] * chunks
        decomposition = filtered

        # submit each ensemble
        index     = 0
        submitted = 0
        for i, merge in enumerate (decomposition):

          # set suffix
          suffix = suffix_format % ('e', i + 1)

          # set label
          label = self.label (level, type, suffix=suffix)

          # initialize ensemble job
          ensemble = ''

          # set batch and merge in parallelization
          parallelization.batch = len (blocks [0][0])
          parallelization.merge = merge

          # submit each block
          for block, batches in enumerate (blocks [submitted : submitted + merge]):

            # header for the subensemble job
            if local.block != None:
              ensemble += '\n# === BLOCK %d\n' % block

            # initialize subensemble job
            subensemble = ''

            # determine the shape of a subblock
            shape = local.get_shape (parallelization.nodes)

            # add corner initialization
            if shape != None:
              subensemble += local.corners % { 'block' : block, 'shape' : shape } + '\n'

            # submit each batch
            for corner, batch in enumerate (batches):

              # increment 'index' counter
              index += 1

              # header for the batch job
              subensemble += '\n# === BATCH JOB %d' % index

              # additional header information
              if local.block != None:
                subensemble += ' [block %d, corner %d]' % (block, corner)

              # end of header for the batch job
              subensemble += '\n'
              
              # append additional parameters to 'args'
              jobs = []
              for args in batch:

                # add batch job of 'shape' to 'corner' within block which is part of an entire ensemble
                jobs.append ( self.wrap (self.job (args, block, corner, shape), args ['sample']) )

              # construct batch job
              batch = '\n'.join (jobs)

              # add timer
              if local.timer:
                batch = local.timer.rstrip() % { 'job' : '\n\n' + batch + '\n', 'timerfile' : self.timerfile + suffix_format % ('b', index) }

              # fork to background (such that other batch jobs in subensemble could proceed)
              if subblocks > 1:
                batch = self.fork (batch)

              # add batch job to the subensemble
              subensemble += batch
            
            # add synchronization
            if subblocks > 1:
              subensemble += self.sync ()

            # add block booting and block freeing
            subensemble = self.boot (subensemble, block)

            # fork to background (such that other subensemble jobs in ensemble could proceed)
            if merge > 1:
              subensemble = self.fork (subensemble)

            # add batch job to the ensemble
            ensemble += subensemble
          
          # add synchronization
          if merge > 1:
            ensemble += self.sync()

          # adjust parallelization according to the number of subblocks
          parallelization.nodes *= subblocks
          parallelization.cores *= subblocks
          
          # submit
          self.execute ( self.submit (ensemble, parallelization, label, directory, suffix=suffix, boot=0, timer=0), directory )

          # update 'submitted' counter
          submitted += size

        # empty queue
        self.batch = []

        # return information about ensembles
        from helpers import intf
        info = [ '%s (%s N)' % ( intf (subblocks * merge), intf (parallelization.nodes * merge) ) for merge in decomposition ]
        return ' + '.join (info) + (' [not fully utilized]' if not utilized else '')
    
    return ''

  # check if the job is finished
  # (required only for non-interactive sessions)
  def finished (self, level, type, sample):
    
    # get directory
    directory = self.directory ( level, type, sample )

    # check if the status file exists
    return os.path.exists ( os.path.join (directory, self.statusfile) )

  # read 'timerfile' from 'directory' and return runtime
  def runtime (self, directory, timerfile):

    timerfilepath = os.path.join (directory, timerfile)
    if os.path.exists (timerfilepath):
      with open ( timerfilepath, 'r' ) as f:
        lines = f.readlines()
        if len (lines) >= 3:
          line = lines [-3]
          if line.strip().split(' ') [0] == 'real':
            return float ( line.strip().split(' ') [-1] )

    return None

  # report timer results
  def timer (self, level, type, sample=None):

    if sample == None:

      # get directory
      directory = self.directory ( level, type )

      # get all timerfiles
      from glob import glob
      timerfiles = sorted ( glob ( os.path.join (directory, self.timerfile + '*') ) )

      # read and return runtimes
      return [ self.runtime ( directory, os.path.basename (timerfile) ) for timerfile in timerfiles ]

    else:
      
      # get directory
      directory = self.directory ( level, type, sample )
      
      # read and return runtime
      return self.runtime (directory, self.timerfile)

  # read 'timerfile' from 'directory' and extract efficiency
  def efficiencies (self, level, type, sample='all'):

    if sample == 'all':

      # get directory
      directory = self.directory ( level, type )

      # get all timerfiles
      from glob import glob
      timerfiles = sorted ( glob ( os.path.join (directory, self.timerfile + '*') ) )

      # read and return runtimes
      return [ self.efficiency (file=timerfile) for timerfile in timerfiles ]

    else:

      return self.efficiency (level, type, sample)

  # check if the loaded result is invalid
  def invalid (self, results):
    return 0

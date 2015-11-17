
# # # # # # # # # # # # # # # # # # # # # # # # # #
# PyMLMC: Python Multi-Level Monte Carlo (MLMC) wrapper
# TODO: add paper, description and link
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import os
import sys
import time

# === local imports

from config import *
from status import *
from mc import *
from indicators import *
from errors import *
import helpers
import local

# === MLMC class

class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, config):
    
    # store configuration
    self.config = config
    
    # finalize configuration setup
    self.config.setup ()
    
    # parse input parameters
    self.params = helpers.parse ()
    
    # status
    self.status = Status ()
    
    # setup solver
    self.config.solver.setup (self.params, self.config.root, self.config.deterministic)

    # setup scheduler
    self.config.scheduler.setup (self.config.levels, self.config.levels_types, self.config.works, self.config.ratios, self.config.solver.sharedmem )

    # setup samples
    self.config.samples.setup ( self.config.levels, self.config.works )
    
    # indicators
    self.indicators = Indicators ( self.config.solver.indicator, self.config.levels, self.config.levels_types )
    
    # errors
    self.errors = Errors (self.config.levels)

    # availability
    self.available = 0
    
    # submission file name
    self.submission_file = 'queue.dat'
  
  # change root of the MLMC simulation
  def chroot (self, root):
    
    self.config.root = root
    self.config.solver.root = root
  
  # MLMC simulation
  def simulation (self):

    # check for consistency
    if self.params.restart and self.params.proceed:
      helpers.error ('Both \'-r\' (--restart) and \'-p\' (--proceed) were specified.', advice='Use either of the options, not both.')

    # initial phase
    if self.params.restart:
      self.init ()

    # proceed with the existing simulation (no modification in setup)
    if self.params.proceed:
      self.proceed ()

    # recursive updating phase
    self.update()

    # query for progress
    helpers.query ('Continue with data analysis?')
    print
  
  # initial phase
  def init (self):
    
    # initialize, report, validate, and save the required number of samples
    self.config.samples.init     ()
    self.config.samples.report   ()
    self.config.samples.validate ()
    if not self.config.deterministic:
      self.config.samples.save     ()
    
    # initialize errors
    if not self.config.deterministic:
      self.errors.init ()
    
    # make indices for the required number of samples
    self.config.samples.make ()
    
    # distribute initial samples
    self.config.scheduler.distribute ()
      
    # query for progress
    helpers.query ('Submit jobs?')

    # compute initial samples
    self.run ()
    
    # update the computed number of samples
    self.config.samples.append ()

    # save status of MLMC simulation
    self.status.save (self.config)
    
    # for clusters: if non-interactive session -> exit
    if local.cluster and not self.params.interactive:
      print
      print ' :: INFO: Non-interactive mode specified -> exiting.'
      print '  : -> Run PyMLMC with \'-i\' option for an interactive mode.'
      print
      sys.exit ()
  
  # iterative updating phase
  def update (self):
    
    while True:
      
      # load MLMC simulation
      self.load ()
      
      # deterministic simulations are not suppossed to be updated
      if self.config.deterministic:
        return
      
      # compute, report, and save error indicators
      self.indicators.compute (self.mcs, self.config.samples.indices.loaded)
      self.indicators.report  ()
      self.indicators.save    ()

      # query for progress
      helpers.query ('Continue?')

      # compute, report, and save errors
      self.errors.compute (self.indicators, self.config.samples.counts)
      self.errors.report  ()
      self.errors.save    ()
      
      # report speedup (MLMC vs MC)
      self.errors.speedup (self.config.works)

      # query for progress
      helpers.query ('Continue?')

      # report number of samples used so far
      self.config.samples.report ()

      # check if the simulation is already finished
      if self.config.samples.finished (self.errors):
        print
        print ' :: Simulation finished.'
        self.status.save (self.config)
        return

      # update, report, and validate the required number of samples
      if self.errors.available and self.indicators.available:
        self.config.samples.update   (self.errors, self.indicators)
        self.config.samples.report   ()
        self.config.samples.validate ()
      
      # for interactive sessions
      if self.params.query:

        # query user for additional input
        while self.query():

          # check if the simulation is already finished
          if self.config.samples.finished (self.errors):
            print
            print ' :: Simulation finished.'
            self.status.save (self.config)
            return

          # otherwise update, report, and validate the number of samples
          if self.errors.available and self.indicators.available:
            self.config.samples.update   (self.errors, self.indicators)
            self.config.samples.report   ()
            self.config.samples.validate ()
          else:
            helpers.warning ('indicators not available - samples can not be updated')

      # for non-interactive sessions, proceed immediately
      else:
        if self.errors.available and self.indicators.available:
          self.config.samples.update   (self.errors, self.indicators)
          self.config.samples.report   ()
          self.config.samples.validate ()
        else:
          helpers.warning ('indicators or errors not available - samples can not be updated')

      # check if samples are available
      if not self.config.samples.available:
        helpers.warning ('samples not available -> exiting simulation...')
        return

      # save the required number of samples
      self.config.samples.save ()
      
      # make indices for the required number of samples
      self.config.samples.make ()
      
      # distribute required samples
      self.config.scheduler.distribute ()

      # query for progress
      helpers.query ('Submit jobs?')

      # compute required samples
      self.run ()
      
      # update the computed number of samples
      self.config.samples.append ()
      
      # save MLMC simulation
      self.save ()
      
      # for clusters: if non-interactive session -> exit
      if local.cluster and not self.params.interactive:
        print
        print ' :: INFO: Non-interactive mode specified -> exiting.'
        print '  : -> Run PyMLMC with \'-i\' option for an interactive mode.'
        print
        sys.exit ()
      
      # otherwise, sleep a bit
      else:
        time.sleep(5)

  # proceed with the existing simulation (no modification in setup)
  def proceed (self):

    # load MLMC simulation
    self.load ()

    # report number of samples used so far
    self.config.samples.report ()

    # revert the previous required number of samples
    # TODO: implement this!
    self.config.samples.revert ()

    # report the reverted number of samples
    self.config.samples.report ()

    # make indices for the required number of samples
    self.config.samples.make ()

    # distribute required samples
    self.config.scheduler.distribute ()

    # query for progress
    helpers.query ('Submit jobs?')

    # compute required samples
    self.run ()

    # update the computed number of samples
    self.config.samples.append ()

    # save MLMC simulation
    self.save ()

    # for clusters: if non-interactive session -> exit
    if local.cluster and not self.params.interactive:
      print
      print ' :: INFO: Non-interactive mode specified -> exiting.'
      print '  : -> Run PyMLMC with \'-i\' option for an interactive mode.'
      print
      sys.exit ()

  # create MC objects
  def create_MCs (self, indices):
    self.mcs = []
    for level, type in self.config.levels_types:
      self.mcs.append ( MC ( MC_Config (self.config, level, type, indices [level]), self.params, self.config.scheduler.parallelizations [level] [type] ) )
  
  # run MC estimates
  def run (self):
    
    # create MC simulations
    self.create_MCs (self.config.samples.indices.additional)
    
    # report samples that will be computed
    print
    print ' :: SAMPLES TO COMPUTE:',
    for count in self.config.samples.counts.additional:
      print helpers.intf (count, table=0), 
    print
    
    # validate MC simulations
    for mc in self.mcs:
      mc.validate ()

    header    = '  :  LEVEL  |   TYPE   |  RESOLUTION  |  SAMPLES  |  HARDWARE  |'
    separator = '  :------------------------------------------------------------|'
    if local.cluster:
      header    += '  WALLTIME  |  BATCH  |  JOBS  |'
      separator += '-------------------------------|'
      if local.ensembles:
        header    += '  MERGE  |  ENSEMBLES  '
        separator += '-----------------------'
    print header
    print separator

    # initialize submission file
    if not self.config.deterministic:
      f = open (self.submission_file, 'wa')
      f.write (header + '\n')
      f.write (separator + '\n')

    # run MC simulations and update submission file
    for mc in self.mcs:
      info = mc.run ()
      f.write (info + '\n')

    # finalize submission file
    if not self.config.deterministic:
      f.write ('\n')
      f.close()
  
  # query user for additional information
  def query (self):
    return self.config.samples.query ()
  
  # check if MC estimates are already available and report
  def join (self):

    from helpers import intf

    print
    self.finished = 1

    # deterministic reporting
    if self.config.deterministic:

      print ' :: STATUS of simulation:'
      format = '  : %s'

      # for all MC simulations
      for mc in self.mcs:

        # check how many samples are still pending
        pending = mc.pending()

        # if simulation is finished, report runtime
        if pending == 0:

          runtime = mc.timer (self.config.scheduler.batch)
          if runtime != None:
            runtimestr = time.strftime ( '%H:%M:%S', time.gmtime (runtime) )
            walltime   = self.status.list ['walltimes'] [mc.config.level] [mc.config.type]
            if walltime != 'unknown':
              percent = round ( 100 * (runtime / 3600) / walltime )
              print format % ('Completed in ' + runtimestr + (' [%2d%%]' % percent) )
            else:
              print format % ('Completed in ' + runtimestr)
          else:
            print format % 'Completed in N/A'

        # report if some simulations are pending
        else:

          self.finished = 0
          print format % 'Pending'


    # stochastic reporting
    else:

      print ' :: STATUS of MC simulations:'
      print '  :  LEVEL  |   TYPE   |  SAMPLES  |  RUNTIME  |  USAGE  |  PENDING  |'
      print '  :------------------------------------------------------------------|'
      format = '  :      %d  |  %s  |     %s  |  %s  |  %s  |    %s   |'

      # for all MC simulations
      for mc in self.mcs:

        # check how many samples are still pending
        pending = mc.pending()

        args = ( mc.config.level, [' FINE ', 'COARSE'] [mc.config.type], intf(len(mc.config.samples), table=1) )

        # if all samples are finished, report runtime
        if pending == 0:

          runtime = mc.timer (self.config.scheduler.batch)
          if runtime != None:
            runtimestr = time.strftime ( '%H:%M:%S', time.gmtime (runtime) )
            walltime   = self.status.list ['walltimes'] [mc.config.level] [mc.config.type]
            if walltime != 'unknown':
              percent = round ( 100 * (runtime / 3600) / walltime )
              print format % ( args + ( runtimestr, '[%2d%%]' % percent, '    ') )
            else:
              print format % ( args + ( runtimestr, '     ', '    ') )
          else:
            print format % ( args + ( '  N/A  ', '     ', '    ') )

        # report if some simulations are pending
        else:

          self.finished = 0
          print format % ( args + ( '       ', '     ', intf (pending, table=1), ) )
    
    if not self.finished:
      # issue a warning and query for progress
      helpers.query ('Ignore and continue nevertheless?', warning='Some simulations are still pending')

  # save MLMC simulation
  def save (self):
    
    # save status of MLMC simulation
    self.status.save (self.config)
  
  # load MLMC simulation
  def load (self):
    
    # load status of MLMC simulation
    self.status.load (self.config)
    
    # recreate MC simulations
    self.create_MCs (self.config.samples.indices.computed)
    
    # if non-interactive session -> wait for jobs to finish
    if not self.params.interactive:
      self.join ()

    # load the results from MC simulations and report
    from helpers import intf
    print
    print ' :: LOADING RESULTS...'
    print '  :  LEVEL  |   TYPE   |  SAMPLES  |  LOADED  |  FAILED  |  PENDING  |'
    print '  :------------------------------------------------------------------|'
    format = '  :      %d  |  %s  |     %s  |   %s   |   %s   |    %s   |'

    # candidate for the coarsest level
    self.L0 = None

    # load all levels
    for level in self.config.levels:

      loaded = [None, None]

      # load both types
      for type in reversed (self.config.types (level)):

        mc = self.mcs [ self.config.pick [level] [type] ]
        pending = mc.pending()
        loaded [type] = mc.load ()

        # check if at least one sample at some level with type FINE
        if mc.available and mc.config.type == self.config.FINE:
          self.available = 1

        # report
        typestr    = [' FINE ', 'COARSE'] [mc.config.type]
        samplesstr = intf(len(mc.config.samples), table=1)
        loadedstr  = intf (len (loaded [type]), table=1, empty=1)
        failedstr  = intf (len (mc.config.samples) - len (loaded [type]), table=1, empty=1)
        pendingstr = intf (pending, table=1, empty=1)
        print format % (mc.config.level, typestr, samplesstr, loadedstr, failedstr, pendingstr)

      # loading is level-dependent (i.e. for non-coarsest levels, samples of both types should be loaded)
      if self.L0 == None:
        if len (loaded [self.config.FINE]) > 0:
          self.config.samples.indices.loaded [level] = loaded [self.config.FINE]
          self.L0 = level
        else:
          self.config.samples.indices.loaded [level] = []
      else:
        self.config.samples.indices.loaded [level] = list ( set (loaded [self.config.FINE]) & set (loaded [self.config.COARSE]) )

      # compute auxiliary counts
      self.config.samples.counts.loaded [level] = len (self.config.samples.indices.loaded [level])
      self.config.samples.counts.failed [level] = self.config.samples.counts.computed [level] - self.config.samples.counts.loaded [level]

    # report how many pairs of fine and course samples were loaded
    print
    print ' :: LOADED PAIRS (FINE & COARSE)...'
    print '  :  LEVEL  |  SAMPLES  |  LOADED  |  FAILED  |'
    print '  :-------------------------------------------|'
    format = '  :      %d  |     %s  |   %s   |   %s   |'
    for level in self.config.levels:
      loadedstr = intf (self.config.samples.counts.loaded [level], table=1, empty=1)
      failedstr = intf (self.config.samples.counts.failed [level], table=1, empty=1)
      print format % (mc.config.level, intf (self.config.samples.counts.computed [level], table=1), loadedstr, failedstr)

    # query for progress
    helpers.query ('Continue?')

  # assemble MC and MLMC estimates
  def assemble (self, stats):

    print
    print ' :: ASSEMBLING:'

    import copy

    # check if statistics can be assembled (at least one sample at some level with type 0)
    if not self.available:
      helpers.error ('Statistics can not be assembled')
    
    # assemble MC estimates on all levels and types for each statistic
    print '  : MC estimates...'
    for mc in self.mcs:
      mc.assemble (stats, self.config.samples.indices.loaded [mc.config.level])

    # assemble differences of MC estimates between type = 0 and type = 1 on all levels for each statistic
    print '  : Differences of MC estimates...'
    self.diffs = [ {} for level in self.config.levels ]
    for name in [stat.name for stat in stats]:

      # mark all levels as unavailable until the valid coarsest level L0
      for level in self.config.levels [0 : self.L0]:
        self.diffs [level] [name] = None

      # coarsest level difference is just a plain MC estimate
      self.diffs [self.L0] [name] = copy.deepcopy (self.mcs [ self.config.pick [self.L0] [self.config.FINE] ] .stats [name])

      # assemble differences of the remaining levels
      for level in self.config.levels [self.L0 + 1 : ]:

        # if at least one sample from that level is available
        if self.config.samples.counts.loaded [level] != 0:
          self.diffs [level] [name]  = copy.deepcopy (self.mcs [ self.config.pick [level] [self.config.FINE  ] ] .stats [name])
          self.diffs [level] [name] -=                self.mcs [ self.config.pick [level] [self.config.COARSE] ] .stats [name]

        # else mark level as unavailable
        else:
          self.diffs [level] [name] = None

    # assemble MLMC estimates (sum of differences for each statistic)
    print '  : MLMC estimates...'
    self.stats = {}
    for name in [stat.name for stat in stats]:

      # copy coarsest difference
      self.stats [name] = copy.deepcopy (self.diffs [self.L0] [name])

      # add remaining differences
      for diff in self.diffs [self.L0 + 1 : ]:
        if diff [name] != None:
          self.stats [name] += diff [name]

    print '  : DONE'
    print
  
  # report computed statistics (mostly used only for debugging)
  def report (self):
    
    for stat in self.stats:
      print
      print ' :: STATISTIC: %s' % stat
      print self.stats [stat]


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
    self.config.samples.setup ( self.config.levels, self.config.works, self.params.tolerate )

    # indicators
    self.indicators = Indicators ( self.config.solver.indicator, self.config.solver.distance, self.config.levels, self.config.levels_types, self.config.pick )
    
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

    # report config
    self.config.report ()

    # query for progress
    helpers.query ('Continue?')

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

    # set iteration to 0 ('initial')
    self.config.iteration = 0

    # initialize, report, validate, and save the required number of samples
    self.config.samples.init     ()
    if not self.config.deterministic:
      self.config.samples.report   ()
    self.config.samples.validate ()
    
    # make indices for the required number of samples
    self.config.samples.make ()
    
    # distribute initial samples
    self.config.scheduler.distribute ()
    
    # query for progress
    if self.params.simulate:
      if self.config.deterministic:
        helpers.query ('Simulate (no actual submissions) job submission?')
      else:
        helpers.query ('Simulate (no actual submissions) initial job submission?')
    else:
      if self.config.deterministic:
        helpers.query ('Submit job?')
      else:
        helpers.query ('Submit initial jobs?')

    # compute initial samples
    self.run ()

    # save status of MLMC simulation
    self.save ()
    
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

      # update the computed number of samples
      self.config.samples.append ()

      # compute, report, and save error indicators
      self.indicators.compute (self.mcs, self.config.samples.indices.loaded)
      self.indicators.report  ()
      self.indicators.save    (self.config.iteration)

      # query for progress
      helpers.query ('Continue?')

      # compute, report, and save errors
      self.errors.compute (self.indicators, self.config.samples.counts)
      self.errors.report  ()
      self.errors.save    (self.config.iteration)
      
      # report speedup (MLMC vs MC)
      self.errors.speedup (self.indicators, self.config.works, self.config.samples.counts)

      # query for progress
      helpers.query ('Continue?')

      # check if we are on the same machine
      if self.status.list ['cluster'] != local.name:
        warning = 'Simulation machine [%s] differs from this machine [%s]' % (self.status.list ['cluster'], local.name)
        message = 'Skip update phase?'
        if helpers.query (message, warning=warning, exit=0) == 'y':
          return

      # recursively query user for input for automated optimal sample adjustments
      while True:

        # return if the simulation is already finished
        if self.config.samples.finished (self.errors):

          # report final number of samples
          self.config.samples.strip  ()
          self.config.samples.report ()
          
          print
          print ' :: Simulation finished.'

          return

        # update, report, and validate the computed/required/pending number of samples
        if self.errors.available and self.indicators.available:

          self.config.samples.update   (self.errors, self.indicators)
          self.config.samples.report   ()
          self.config.samples.validate ()

        # if samples can not be updated, display warning and skip user input query
        else:

          helpers.warning ('indicators or errors not available - samples can not be updated')
          break

        # for interactive sessions
        if self.params.query:

          # query user for input
          modified = self.query()

          # if no changes were requested, proceed
          if not modified:
            break

        # for non-interactive sessions, proceed immediately
        else:
          break

      # recursively query user for manual sample specification or adjustment
      while True:

        # for interactive sessions
        if self.params.query:

          # query user for input
          manual = self.config.samples.manual()

          # always report manual sample specification or adjustment
          if manual:
            self.config.samples.available = 1
            self.config.samples.report   ()
            self.config.samples.validate ()

          # proceed if no specification or adjustment were requested
          if not manual:
            break

        # for non-interactive sessions, proceed immediately
        else:
          break

      # check if samples are available
      if not self.config.samples.available:
        helpers.warning ('samples not available -> exiting simulation...')
        return
      
      # make indices for the required number of samples
      self.config.samples.make ()
      
      # distribute required samples
      self.config.scheduler.distribute ()

      # query for progress
      if self.params.simulate:
        helpers.query ('Simulate additional job submission (no actual submissions)?')
      else:
        helpers.query ('Submit additional jobs?')

      # increment iteration
      self.config.iteration += 1

      # compute required samples
      self.run ()

      # save status of MLMC simulation
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
    
    # distribute required samples
    self.config.scheduler.distribute ()

    # query for progress
    helpers.query ('Submit jobs?')

    # compute required samples
    self.run ()

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
  def create_MCs (self, indices, iteration):
    self.mcs = []
    for level, type in self.config.levels_types:
      self.mcs.append ( MC ( MC_Config (self.config, level, type, indices [level], iteration), self.params, self.config.scheduler.parallelizations [level] [type] ) )
  
  # run MC estimates
  def run (self):
    
    # create MC simulations
    self.create_MCs (self.config.samples.indices.additional, self.config.iteration)
    
    # report samples that will be computed
    if not self.config.deterministic:
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
      header    += '  WALLTIME  |  BATCH  ->  JOBS   |'
      separator += '---------------------------------|'
      if local.ensembles and not self.config.deterministic:
        header    += '  MERGE  ->  ENSEMBLES  '
        separator += '------------------------'
    print header
    print separator

    # initialize submission file
    if self.config.deterministic:
      f = open (self.submission_file, 'wa')
    else:
      f = open (self.submission_file + '.%d' % self.config.iteration, 'wa')

    f.write (header + '\n')
    f.write (separator + '\n')

    # run MC simulations and update submission file
    for mc in self.mcs:
      info = mc.run ()
      f.write (info + '\n')

    # finalize submission file
    f.write ('\n')
    f.close()
  
  # query user for additional information
  def query (self):

    modified = self.config.samples.query ()
    return modified

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
          if runtime ['max'] != None:
            runtimestr = time.strftime ( '%H:%M:%S', time.gmtime (runtime ['max']) )
            walltime   = self.status.list ['walltimes'] [mc.config.level] [mc.config.type]
            if walltime != 'unknown':
              walltimestr = time.strftime ( '%H:%M:%S', time.gmtime (walltime * 3600) )
              percent = round ( 100 * (runtime ['max'] / 3600) / walltime )
              print format % ('Completed in ' + runtimestr + (' [%2d%% of %s]' % (percent, walltimestr)) )
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


      header    = '  :  LEVEL  |   TYPE   |  SAMPLES  |  FINISHED  |  PENDING  |  WALLTIME  |        RUNTIME        |     USAGE     |     BUDGET    |   EFFICIENCY  |'
      separator = '  :----------------------------------------------------------------------------------------------------------------------------------------------|'
      format = '  :      %d  |  %s  |    %s  |    %s   |   %s   |  %s  |  %s - %s  |  %s - %s  |  %s - %s  |  %s - %s  |'

      header    += '  BATCH  |     BATCH RUNTIME     |'
      separator += '---------------------------------|'
      format    += '  %s  |  %s - %s  |'

      print ' :: STATUS of MC simulations:'
      print header
      print separator

      # for all MC simulations
      for mc in self.mcs:

        # check how many samples are already finished
        finished = mc.finished()

        # check how many samples are still pending
        pending = mc.pending()

        args = ( mc.config.level, [' FINE ', 'COARSE'] [mc.config.type], intf(len(mc.config.samples), table=1), intf (finished, table=1, empty=1), intf (pending, table=1, empty=1) )

        # we are not finished if at least one simulation is pending
        if pending > 0:
          self.finished = 0

        # report walltime
        walltime_sample = self.status.list ['walltimes'] [mc.config.level] [mc.config.type]
        if walltime_sample != 'unknown':
          walltime_sample_str = time.strftime ( '%H:%M:%S', time.gmtime (walltime_sample * 3600) )
          args += (walltime_sample_str, )
        else:
          args += ('   N/A  ', )

        # if some samples are finished, report runtimes, budget, efficiency, batching, etc.
        if finished > 0:

          # parallelization
          parallelization = self.status.list ['parallelization'] [mc.config.level] [mc.config.type]

          # runtimes, walltime usage, budget usage, etc. of individual samples
          runtime_sample = mc.timer ()
          if runtime_sample ['min'] != None and runtime_sample ['max'] != None:

            # runtimes
            min_runtime_sample_str = time.strftime ( '%H:%M:%S', time.gmtime (runtime_sample ['min']) )
            max_runtime_sample_str = time.strftime ( '%H:%M:%S', time.gmtime (runtime_sample ['max']) )
            args += ( min_runtime_sample_str, max_runtime_sample_str )

            # walltime usage
            if walltime_sample != 'unknown':
              walltime_sample_percent_min = round ( 100 * (runtime_sample ['min'] / 3600) / walltime_sample )
              walltime_sample_percent_max = round ( 100 * (runtime_sample ['max'] / 3600) / walltime_sample )
              args += ( '%3d%%' % walltime_sample_percent_min, '%3d%%' % walltime_sample_percent_max )
            else:
              args += ('    ', '    ')

            # budget usage
            budget_sample             = float (self.config.works [mc.config.level - mc.config.type]) / parallelization
            budget_sample_percent_min = round ( 100 * (runtime_sample ['min'] / 3600) / budget_sample )
            budget_sample_percent_max = round ( 100 * (runtime_sample ['max'] / 3600) / budget_sample )
            args += ( '%3d%%' % budget_sample_percent_min, '%3d%%' % budget_sample_percent_max )

          # default values if runtime measurements are not available
          else:

            args += ( '   N/A  ', '   N/A  ' )

            # LEGACY: instead, report walltime and budget usage for entire batches
            batch         = self.status.list ['batch'] [mc.config.level] [mc.config.type]
            runtime_batch = mc.timer (batch=1)
            if runtime_batch ['min'] != None and runtime_batch ['max'] != None:

              # walltime usage
              if walltime_sample != 'unknown':
                walltime_batch = walltime_sample * batch if batch != None else walltime_sample
                walltime_batch_percent_min  = round ( 100 * (runtime_batch  ['min'] / 3600) / walltime_batch )
                walltime_batch_percent_max  = round ( 100 * (runtime_batch  ['max'] / 3600) / walltime_batch )
                args += ( '%3d%%' % walltime_batch_percent_min, '%3d%%' % walltime_batch_percent_max )
              else:
                args += ('    ', '    ')

              # budget usage
              budget_sample  = float (self.config.works [mc.config.level - mc.config.type]) / parallelization
              budget_batch   = budget_sample * batch if batch != None else budget_sample
              budget_batch_percent_min = round ( 100 * (runtime_batch ['min'] / 3600) / budget_batch )
              budget_batch_percent_max = round ( 100 * (runtime_batch ['max'] / 3600) / budget_batch )
              args += ( '%3d%%' % budget_batch_percent_min, '%3d%%' % budget_batch_percent_max )

            else:
              args += ( '    ', '    ' )
              args += ( '    ', '    ' )

          # efficiency
          efficiency_sample = mc.efficiency ()
          if efficiency_sample ['min'] != None and efficiency_sample ['max'] != None:
            args += ( '%3d%%' % efficiency_sample ['min'], '%3d%%' % efficiency_sample ['max'] )
          
          # LEGACY: instead, report efficiency for entire batches
          else:
            efficiency_batch = mc.efficiency (batch=1)
            if efficiency_batch ['min'] != None and efficiency_batch ['max'] != None:
              args += ( '%3d%%' % efficiency_batch ['min'], '%3d%%' % efficiency_batch ['max'] )
            else:
              args += ( '    ', '    ' )

          # batch
          batch     = self.status.list ['batch'] [mc.config.level] [mc.config.type]
          batch_str = helpers.intf (batch, table=1, empty=1)
          args += (batch_str, )

          # runtimes, usage, budget of the entire batches
          runtime_batch  = mc.timer (batch=1)
          if runtime_batch ['min'] != None and runtime_batch ['max'] != None:

            # runtimes
            min_runtime_batch_str = time.strftime ( '%H:%M:%S', time.gmtime (runtime_batch  ['min']) )
            max_runtime_batch_str = time.strftime ( '%H:%M:%S', time.gmtime (runtime_batch  ['max']) )
            args += ( min_runtime_batch_str, max_runtime_batch_str )

            '''
            # walltime usage
            if walltime_sample != 'unknown':
              walltime_batch = walltime_sample * batch if batch != None else walltime_sample
              walltime_batch_percent_min  = round ( 100 * (runtime_batch  ['min'] / 3600) / walltime_batch )
              walltime_batch_percent_max  = round ( 100 * (runtime_batch  ['max'] / 3600) / walltime_batch )
            '''

          # default values if runtime measurements are not available
          else:
            args += ( '   N/A  ', '   N/A  ' )

          print format % args

        # report that all simulations are pending
        else:

          args += ( '        ', '        ', '    ', '    ', '    ', '    ', '    ', '    ' )
          batch     = self.status.list ['batch'] [mc.config.level] [mc.config.type]
          batch_str = helpers.intf (batch, table=1, empty=1)
          args += ( batch_str, '        ', '        ' )
          print format % args

    if not self.finished:
      # issue a warning and query for progress
      helpers.query ('Ignore and continue nevertheless?', warning='Some simulations are still pending')

  # save MLMC simulation
  def save (self):
    
    # save status of MLMC simulation
    self.status.save (self.config)

    # save samples history
    if not self.config.deterministic:
      self.config.samples.save (self.config.iteration)
  
  # load MLMC simulation
  def load (self):
    
    # load status of MLMC simulation
    if self.params.verbose:
      self.status.load (self.config)
    else:
      try:
        self.status.load (self.config)
      except:
        message = 'MLMC status could not be loaded from'
        details = os.path.join (self.config.root, self.status.status_file + '*')
        advice  = 'Run PyMLMC with \'-v 1\' option for verbose mode or with \'-r\' option to restart the simulation'
        helpers.error (message, details, advice)

    if not self.config.deterministic:

      # load samples history
      self.config.samples.load (self.config)

      # load indicators history
      self.indicators.load (self.config)

      # load errors history
      self.errors.load (self.config)

    # recreate MC simulations
    self.create_MCs (self.config.samples.indices.combined, self.config.iteration)
    
    # if non-interactive session -> wait for jobs to finish
    if not self.params.interactive:
      self.join ()

    # load the results from MC simulations and report
    from helpers import intf
    print
    print ' :: LOADING RESULTS:'
    print '  :  LEVEL  |   TYPE   |  SAMPLES  |  LOADED  |  FAILED  |  PENDING  |'
    print '  :------------------------------------------------------------------|'
    format = '  :      %d  |  %s  |    %s  |   %s  |   %s  |   %s   |'

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
      self.config.samples.counts.failed [level] = self.config.samples.counts.combined [level] - self.config.samples.counts.loaded [level]

    # report how many pairs of fine and course samples were loaded
    print
    print ' :: LOADED PAIRS (FINE & COARSE):'
    print '  :  LEVEL  |  SAMPLES  |  LOADED  |  FAILED  |'
    print '  :-------------------------------------------|'
    format = '  :      %d  |    %s  |   %s  |   %s  |'
    for level in self.config.levels:
      loadedstr = intf (self.config.samples.counts.loaded [level], table=1, empty=1)
      failedstr = intf (self.config.samples.counts.failed [level], table=1, empty=1)
      print format % (mc.config.level, intf (self.config.samples.counts.combined [level], table=1), loadedstr, failedstr)
    
    # report detailed progrees of individual samples
    self.progress ()

    # query for progress
    helpers.query ('Continue?')

  # report dedailed progress of individual samples
  def progress (self):

    yes = helpers.query ('Show detailed progress of individual samples?')

    if not yes:
      return

    print
    print ' :: PROGRESS: [not yet implemented]'

    # TODO: implement this!

  # assemble MC and MLMC estimates
  def assemble (self, stats, qois='all'):

    print
    print ' :: ASSEMBLING:'

    # report quantities of interest to be assembled
    print '  :',
    for qoi in qois:
      print qoi,
    print

    import copy

    # check if statistics can be assembled (at least one sample at some level with type 0)
    if not self.available:
      helpers.error ('Statistics can not be assembled')
    
    # assemble MC estimates on all levels and types for each statistic
    print '  : MC estimates...'
    for mc in self.mcs:
      mc.assemble (stats, self.config.samples.indices.loaded [mc.config.level], qois)

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


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
    
    # submission file name
    self.submission_file = 'queue.dat'
  
  # change root of the MLMC simulation
  def chroot (self, root):
    
    self.config.root = root
    self.config.solver.root = root
  
  # MLMC simulation
  def simulation (self):
    
    # initial phase
    if self.params.restart:
      self.init ()
    
    # recursive updating phase
    self.update()
    
    # query user for further action
    print
    print ' :: QUERY: Continue with data analysis? [enter \'y\' or press ENTER]'
    input = raw_input ( '  : ' ) or 'y'
    if input != 'y':
      print '  : EXIT'
      print
      sys.exit()
    else:
      print '  : CONTINUE'
  
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
      self.indicators.compute (self.mcs)
      self.indicators.report  ()
      self.indicators.save    ()
      
      # compute, report, and save errors
      self.errors.compute (self.indicators, self.config.samples.counts)
      self.errors.report  ()
      self.errors.save    ()
      
      # report speedup (MLMC vs MC)
      self.errors.speedup (self.config.works)

      # report number of samples used so far (avoid updating as this might not be possible)
      self.config.samples.report   ()

      # check if the simulation is already finished
      if self.config.samples.finished (self.errors):
        print
        print ' :: Simulation finished.'
        self.status.save (self.config)
        return

      '''
      # update, report, and validate the required number of samples
      self.config.samples.update   (self.errors, self.indicators)
      self.config.samples.report   ()
      self.config.samples.validate ()
      '''
      
      # for interactive sessions, query user for additional input
      if self.params.query:
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
            print ' :: WARNING: indicators not available - samples can not be updated'

      # for non-interactive sessions, proceed immediately
      else:
        if self.errors.available and self.indicators.available:
          self.config.samples.update   (self.errors, self.indicators)
          self.config.samples.report   ()
          self.config.samples.validate ()
        else:
          print ' :: WARNING: indicators not available - samples can not be updated'

      # check if samples are available
      if not self.config.samples.available:
        print ' :: WARNING: samples not available -> exiting'
        return

      # save the required number of samples
      self.config.samples.save ()
      
      # make indices for the required number of samples
      self.config.samples.make ()
      
      # distribute additional samples
      self.config.scheduler.distribute ()
      
      # compute additional samples
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
    separator = '  :---------|----------|--------------|-----------|------------|'
    if local.cluster:
      header    += '  WALLTIME  |  BATCH  |  JOBS  |'
      separator += '------------|---------|--------|'
      if local.ensembles:
        header    += '  MERGE  |  ENSEMBLES  '
        separator += '---------|-------------'
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
      print
      print ' :: WARNING: Some simulations are still pending'
      print ' :: QUERY: Ignore and continue nevertheless? [enter \'y\' or press ENTER]'
      input = raw_input ( '  : ' ) or 'y'
      if input != 'y':
        print '  : EXIT'
        print
        sys.exit()
      else:
        print '  : CONTINUE'

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

    from helpers import intf
    # load the results from MC simulations
    print
    print ' :: LOADING RESULTS...'
    print '  :  LEVEL  |   TYPE   |  SAMPLES  |  LOADED  |  FAILED  |'
    print '  :------------------------------------------------------|'
    format = '  :      %d  |  %s  |     %s  |   %s   |   %s   |'
    self.available = 1
    for mc in self.mcs:
      loaded, failed = mc.load ()
      if loaded == 0:
        self.available = 0
      typestr = [' FINE ', 'COARSE'] [mc.config.type]
      print format % (mc.config.level, typestr, intf(len(mc.config.samples), table=1), intf (loaded, table=1), intf (failed, table=1) if failed != 0 else '    ')
    print '  : DONE'

    print
    print ' :: QUERY: Continue? [enter \'y\' or press ENTER]'
    input = raw_input ( '  : ' ) or 'y'
    if input != 'y':
      print '  : EXIT'
      print
      sys.exit()
    else:
      print '  : CONTINUE'

  # assemble MC and MLMC estimates
  def assemble (self, stats):

    print
    print ' :: ASSEMBLING:'

    # check if statistics can be assembled
    if not self.available:
      print
      print ' :: ERROR: statistics can not be assembled -> exiting...'
      print
      sys.exit()
    
    # assemble MC estimates on all levels and types for each statistic
    print '  : MC estimates...'
    for mc in self.mcs:
      mc.assemble (stats)

    # assemble differences of MC estimates between type = 0 and type = 1 on all levels for each statistic
    print '  : Differences of MC estimates...'
    #self.diffs = [ { stat.name : self.config.solver.DataClass () for stat in stats } for level in self.config.levels ]
    self.diffs = []
    for level in self.config.levels:
      self.diffs .append ( {} )
      for stat in stats:
        self.diffs [-1] [stat.name] = self.config.solver.DataClass ()
    for name in [stat.name for stat in stats]:
      for mc in self.mcs:
        if mc.config.type == self.config.FINE:   self.diffs [mc.config.level] [name] += mc.stats [ name ]
        if mc.config.type == self.config.COARSE: self.diffs [mc.config.level] [name] -= mc.stats [ name ]

    # assemble MLMC estimates (sum of differences for each statistic)
    print '  : MLMC estimates...'
    self.stats = {}
    for name in [stat.name for stat in stats]:
      self.stats [ name ] = self.config.solver.DataClass ()
      for diff in self.diffs:
        self.stats [ name ] += diff [name]

    print '  : DONE'
  
  # report computed statistics (mostly used only for debugging)
  def report (self):
    
    for stat in self.stats:
      print
      print ' :: STATISTIC: %s' % stat
      print self.stats [stat]

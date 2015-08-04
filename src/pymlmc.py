
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
    self.config.samples.setup ( self.config.levels, self.config.scheduler.works )
    
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
    
    # initialize, validate, and save the required number of samples
    self.config.samples.init     ()
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
      self.errors.report  (self.config.samples.tol)
      self.errors.save    ()
      
      # report speedup (MLMC vs MC)
      self.errors.speedup (self.config.works)
      
      # check if the simulation is already finished 
      if self.config.samples.finished (self.errors):
        print
        print ' :: Simulation finished.'
        self.status.save (self.config)
        return
      
      # update, report, and validate the required number of samples
      self.config.samples.update   (self.errors, self.indicators)
      self.config.samples.report   ()
      self.config.samples.validate ()
      
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
          self.config.samples.update   (self.errors, self.indicators)
          self.config.samples.report   ()
          self.config.samples.validate ()
      
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

    header    = '  :  LEVEL  |   TYPE   |  RESOLUTION  |  SAMPLES  |  HARDWARE  '
    separator = '  :---------|----------|--------------|-----------|------------'
    if local.cluster:
      header    += '|  WALLTIME  |  BATCH  '
      separator += '|------------|---------'
    print header
    print separator

    # run MC simulations
    for mc in self.mcs:
      mc.run ()
    
    # generate submission file
    if not self.config.deterministic:
      f = open (self.submission_file, 'wa')
      f.write (header + '\n')
      f.write (separator + '\n')
      for mc in self.mcs:
        f.write (mc.info() + '\n')
      f.write ('\n')
      f.close()
  
  # query user for additional information
  def query (self):
    return self.config.samples.query ()
  
  # check if MC estimates are already available
  def join (self):
    
    print
    if self.config.deterministic:
      print ' :: STATUS of simulation:'
      format = '  : %s'
    else:
      print ' :: STATUS of MC simulations:'
      format = '  :  level %2d  |  %s  |  %s sample(s)  |  %s'
    
    self.finished = 1
    for mc in self.mcs:
      if self.config.deterministic:
        args = tuple()
      else:
        args = ( mc.config.level, ['  FINE', 'COARSE'] [mc.config.type], intf(len(mc.config.samples)) )
      pending = mc.pending()
      if pending == 0:
        runtime = mc.timer (self.config.scheduler.batch)
        if runtime != None:
          runtimestr = time.strftime ( '%H:%M:%S', time.gmtime (runtime) )
          walltime   = self.status.list ['walltimes'] [mc.config.level] [mc.config.type]
          if walltime != 'unknown':
            percent = round ( 100 * (runtime / 3600) / walltime )
            print format % ( args + ( 'completed in ' + runtimestr + (' [%2d%%]' % percent), ) )
          else:
            print format % ( args + ( 'completed in ' + runtimestr, ) )
        else:
          print format % ( args + ( 'completed in N/A', ) )
      else:
        self.finished = 0
        if self.config.deterministic:
          print format % ( args + ( 'pending', ) )
        else:
          print format % ( args + ( 'pending: %d' % pending, ) )
    
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
    
    # load the results from MC simulations
    print
    print ' :: LOADING RESULTS...'
    for mc in self.mcs:
      mc.load ()
    print '  : DONE'
  
  # assemble MC and MLMC estimates
  def assemble (self, stats):

    print
    print ' :: ASSEMBLING:'

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

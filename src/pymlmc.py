
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
    
    # setup samples
    self.config.samples.setup ( self.config.levels, self.config.works )
    
    # setup scheduler
    self.config.scheduler.setup (self.config.levels, self.config.levels_types, self.config.works, self.config.ratios, self.config.solver.sharedmem )
    
    # indicators
    self.indicators = Indicators ( self.config.solver.indicator, self.config.levels, self.config.levels_types )
    
    # errors
    self.errors = Errors (self.config.levels)
    
    # MLMC results
    self.stats = {}
    
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
      
      # load status of MLMC simulation
      self.status.load (self.config)
      
      # recreate MC simulations
      self.create_MCs (self.config.samples.indices.computed)
      
      # if non-interactive session -> wait for jobs to finish
      if not self.params.interactive:
        self.join ()
      
      # load results
      self.load ()
      
      # deterministic simulations are not suppossed to be updated
      if self.config.deterministic:
        print
        print ' :: Deterministic simulation finished.'
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
      
      # save status of MLMC simulation
      self.status.save (self.config)
      
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
    
    # run MC simulations
    for mc in self.mcs:
      mc.run ()
    
    # generate submission file
    if not self.config.deterministic:
      f = open (self.submission_file, 'wa')
      for mc in self.mcs:
        f.write (mc.info()+'\n')
      f.write ('\n')
      f.close()
  
  # query user for additional information
  def query (self):
    return self.config.samples.query ()
  
  # check if MC estimates are already available
  def join (self):
    
    print
    print ' :: STATUS of MC simulations:'
    
    format = '  :  level %2d  |  %s  |  %s sample(s)  |  %s'
    
    self.finished = 1
    for mc in self.mcs:
      args = ( mc.config.level, ['  FINE', 'COARSE'] [mc.config.type], intf(len(mc.config.samples)) )
      pending = mc.pending()
      if pending == 0:
        runtime    = mc.timer (self.config.scheduler.batch)
        runtimestr = time.strftime ( '%H:%M:%S', time.gmtime (runtime) )
        percent    = round ( runtime / mc.parallelization.walltime )
        print format % ( args + ( 'completed in ' + runtimestr + (' [%3d\%]' % percent), ) )
      else:
        self.finished = 0
        print format % ( args + ( 'pending: %d' % pending, ) )
    
    if not self.finished:
      print
      print ' :: WARNING: Some MC simulations are still pending'
      print ' :: QUERY: Ignore and continue nevertheless? [enter \'y\' or press ENTER]'
      input = raw_input ( '  : ' ) or 'y'
      if input != 'y':
        print '  : EXIT'
        print
        sys.exit()
      else:
        print '  : CONTINUE'
  
  # load the results from MC simulations
  def load (self):
    for mc in self.mcs:
      mc.load ()
  
  # assemble MC and MLMC estimates
  def assemble (self, stats):
    
    # assemble MC estimates
    for mc in self.mcs:
      mc.assemble (stats)
    
    # assemble MLMC estimates
    for name in [stat.name for stat in stats]:
      self.stats [ name ] = self.config.solver.DataClass ()
      for mc in self.mcs:
        if mc.config.type == self.FINE:   self.stats [ name ] += mc.stats [ name ]
        if mc.config.type == self.COARSE: self.stats [ name ] -= mc.stats [ name ]
    
    return self.stats
  
  # report computed statistics (mostly used only for debugging)
  def report (self):
    
    for stat in self.stats:
      print
      print ' :: STATISTIC: %s' % stat
      print self.stats [stat]

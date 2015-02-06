
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

import sys
import time

# === local imports

from mc import *
from indicators import *
from errors import *
import helpers
import local

# === additional Python paths

sys.path.append ( os.path.dirname(__file__) + "/solver" )
sys.path.append ( os.path.dirname(__file__) + "/samples" )
sys.path.append ( os.path.dirname(__file__) + "/scheduler" )
sys.path.append ( os.path.dirname(__file__) + "/stats" )
sys.path.append ( os.path.dirname(__file__) + "/plot" )

# === classes

# configuration class for MLMC simulations
class MLMC_Config (object):
  
  def __init__ (self, id=0):
    vars (self) .update ( locals() )
  
  # used to set solver, discretizations, samples and scheduler
  def set (self, name, value):
    vars (self) .update ( { name : value } )

# MLMC class
class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, config, deterministic=0):
    
    # store configuration
    vars (self) .update ( locals() )
    
    # parse input parameters
    self.params = helpers.parse (deterministic)
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1
    
    # determine levels
    self.levels = range ( len ( config.discretizations ) )
    
    # determine finest level
    self.L = len(self.levels) - 1
    
    # setup required pairs of levels and types
    levels_types_fine   = [ [level, self.FINE]   for level in self.levels [1:] ]
    levels_types_coarse = [ [level, self.COARSE] for level in self.levels [1:] ]
    self.levels_types   = [ [0, self.FINE] ]  + [level_type for levels_types in zip (levels_types_coarse, levels_types_fine) for level_type in levels_types]
    
    # indicators
    self.indicators = Indicators ( self.config.solver.indicator, self.levels, self.levels_types )
    
    # errors
    self.errors = Errors (self.levels)
    
    # works
    # TODO: take into account _differences_ on all levels except the coarsest
    self.works = [ config.solver.work (discretization) for discretization in config.discretizations ]
    
    # core ratios
    self.ratios = [ config.solver.ratio (config.discretizations [self.L], discretization) for discretization in config.discretizations ]
    
    # setup samples
    self.config.samples.setup ( self.levels, self.works )
    
    # setup scheduler
    self.config.scheduler.setup (self.levels, self.levels_types, self.works, self.ratios, config.solver.sharedmem )
    
    # setup solver
    self.config.solver.setup (self.params)
    
    # MLMC results
    self.stats = {}
    
    # status file name
    self.status_file = 'status.dat'
    
    # submission file name
    self.submission_file = 'queue.dat'
  
  # MLMC simulation
  def simulation (self):
    
    # initial phase
    if self.params.restart:
      self.init ()
    
    # recursive updating phase
    self.update()
  
  # initial phase
  def init (self):
    
    # initialize, validate, and save the required number of samples
    self.config.samples.init     ()
    self.config.samples.validate ()
    self.config.samples.save     ()
    
    # initialize errors
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
    self.status_save ()
    
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
      self.status_load ()
      
      # for clusters: if non-interactive session -> wait for jobs to finish
      if local.cluster and not self.params.interactive:
        self.join ()
      
      # load results
      self.load ()
      
      # compute, report, and save error indicators
      self.indicators.compute (self.mcs)
      self.indicators.report  ()
      self.indicators.save    ()
      
      # compute, report, and save errors
      self.errors.compute (self.indicators, self.config.samples.counts)
      self.errors.report  (self.config.samples.tol)
      self.errors.save    ()
      
      # check if the simulation is already finished 
      if self.config.samples.finished (self.errors) or self.params.deterministic:
        print
        print ' :: Simulation finished.'
        self.status_save ()
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
            self.status_save ()
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
      self.status_save ()
      
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
    for level, type in self.levels_types:
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
    self.create_MCs (self.config.samples.indices.computed)
    for mc in self.mcs:
      if not mc.finished ():
        Exception ( ':: ERROR: MC simulations are not yet available')
  
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
  
  # report computed statistics
  def report (self):
    
    for stat in self.stats:
      print
      print ' :: STATISTIC: %s' % stat
      print self.stats [stat]
  
  # save MLMC status
  def status_save (self):
    
    with open ( self.status_file, 'w' ) as f:
      f.write ( 'samples  = [ ' + ''.join ( [ str(self.config.samples.counts.computed [level]) + ', ' for level in self.levels ] ) + ']\n' )
      if not self.params.deterministic:
        f.write ( 'tol      = ' + str (self.config.samples.tol) + '\n' )
      f.write ( 'deterministic = ' + str (self.params.deterministic) + '\n' )
      #f.write ( 'finished = %d' % int(self.config.samples.finished(self.errors)) )
    
    print
    print (' :: INFO: MLMC status saved to status.py') 
  
  # load MLMC status
  def status_load (self):
    
    try:
      
      status = {}
      execfile (self.status_file, globals(), status)
      
      self.config.samples.counts.computed = status ['samples']
      self.config.samples.make ()
      
      self.params.deterministic = int ( status ['deterministic'] )
      if not self.params.deterministic:
        if self.config.samples.tol != status ['tol']:
          print
          print (' :: WARNING: The requested tolerance is different from the tolerance in the in status file.')
          print
        self.config.samples.tol = status ['tol']
      
      print
      print (' :: INFO: MLMC status loaded from %s' % self.status_file)
      print
    
    except:
      
      print
      print (' :: ERROR: MLMC status could not be loaded from %s' % self.status_file)
      print ('  : -> Run PyMLMC with \'-r\' option to restart the simulation')
      print
      
      raise
      sys.exit()


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

# === local imports

from mc import *
from indicators import *
import helpers

# === additional Python paths

sys.path.append ( os.path.dirname(__file__) + "/solver" )
sys.path.append ( os.path.dirname(__file__) + "/samples" )
sys.path.append ( os.path.dirname(__file__) + "/balancer" )
sys.path.append ( os.path.dirname(__file__) + "/stats" )

# === classes

# configuration class for MLMC simulations
class MLMC_Config (object):
  
  def __init__ (self, solver, discretizations, samples, id=1):
    vars (self) .update ( locals() )

# configuration class for MC simulations
class MC_Config (object):
  
  def __init__ (self, mlmc_config, level, type, samples):
    vars (self) .update ( locals() )
    self.solver         = mlmc_config.solver
    self.discretization = mlmc_config.discretizations [level]
    self.id             = mlmc_config.id

# MLMC class
class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, config, params):
    
    # store configuration
    vars (self) .update ( locals() )
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1
    
    # determine levels
    self.levels = range ( len ( config.discretizations ) )
    
    # setup required pairs of levels and types
    self.levels_types  = [ [level, self.FINE]   for level in self.levels      ]
    self.levels_types += [ [level, self.COARSE] for level in self.levels [1:] ]
    
    # indicators
    self.indicators = Indicators ( self.config.solver.indicator, self.levels, self.levels_types )
    
    # works
    self.works = [ config.solver.work (discretization) for discretization in config.discretizations ]
    
    # MLMC results
    self.stats = {}
  
  # MLMC simulation
  def simulation (self):
    
    # initial phase
    if self.params.restart:
      self.init ()
    
    # recursive updating phase
    self.update()
  
  # initial phase
  def init (self):
    
    # load status of MLMC simulation
    self.status_load ()
    
    # initialize and validate the required number of samples
    self.config.samples.init (self.levels, self.works)
    self.config.samples.validate ()
    
    # compute initial samples
    self.run ()
    
    # save status of MLMC simulation
    self.status_save ()
    
    # if non-interactive session, exit
    if not self.params.interactive:
      sys.exit ()
  
  # iterative updating phase
  def update (self):
    
    while True:
      
      # load status of MLMC simulation
      self.status_load ()
      
      # wait for jobs to finish 
      self.join ()
      
      # load results
      self.load ()
      
      # compute and report error indicators
      self.indicators.compute (self.mcs)
      self.indicators.report  ()
      
      # compute and report errors
      self.config.samples.compute_errors (self.indicators)
      self.config.samples.report_errors  ()
      
      # check if the simulation is already finished 
      if self.config.samples.finished ():
        break
      
      # update, validate and report the required number of samples
      self.config.samples.update   ()
      self.config.samples.report   ()
      self.config.samples.validate ()
      
      # for interactive sessions, query user for additional input
      if self.params.interactive:
        while self.query():
          self.config.samples.update   ()
          self.config.samples.report   ()
          self.config.samples.validate ()
      
      # compute additional samples
      self.run ()
      
      # save status of MLMC simulation
      self.status_save ()
      
      if not self.params.interactive:
        sys.exit () 
  
  # create MC objects
  def create_MCs (self):
    self.mcs = []
    for i, (level, type) in enumerate(self.levels_types):
      self.mcs.append ( MC ( MC_Config (self.config, level, type, self.config.samples.indices [level]), self.params ) )
  
  # run MC estimates
  def run (self):
    self.create_MCs ()
    for mc in self.mcs:
      mc.run ()
  
  # query user for additional information
  def query (self):
    return self.config.samples.query ()
  
  # check if MC estimates are already available
  def join (self):
    self.create_MCs ()
    for mc in self.mcs:
      if not mc.finished ():
        Exception ( ':: ERROR: MC simulations are not yet available')
  
  # load the results from MC simulations
  def load (self):
    self.create_MCs ()
    for mc in self.mcs:
      mc.load ()
  
  # assemble MC and MLMC estimates
  def assemble (self, stats):
    
    # assemble MC estimates
    for mc in self.mcs:
      mc.assemble (stats)
    
    # assemble MLMC estimates
    for name in [stat.name for stat in stats]:
      self.stats [ name ] = 0 
      for mc in self.mcs: 
        if mc.config.type == self.FINE:   self.stats [ name ] += mc.stats [ name ]
        if mc.config.type == self.COARSE: self.stats [ name ] -= mc.stats [ name ]
    
    return self.stats
  
  # load MLMC status
  def status_load (self):
   
   print (' :: WARNING: status_load() is not yet implemented.') 
    # TODO
  
  # save MLMC status
  def status_save (self):
    
    print (' :: WARNING: status_save() is not yet implemented.') 
    # TODO

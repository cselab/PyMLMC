
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
    self.solver = solver
    self.discretizations = discretizations
    self.samples = samples
    self.id = id

# configuration class for MC simulations
class MC_Config (object):
  
  def __init__ (self, mlmc_config, level, type, samples):
    vars (self) .update ( locals() )
    self.level   = level
    self.type    = type
    self.samples = samples
    self.id      = mlmc_config.id
    self.solver  = mlmc_config.solver
    self.discretization = mlmc_config.discretizations [level - type]

# MLMC class
class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, config, params):
    
    # store configuration
    vars (self) .update ( locals() )
    self.config = config
    self.params = params
    
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
      self.init()
    
    # recursive updating phase
    self.update()
  
  # initial phase
  def init (self):
    
    self.status_load()
    self.config.samples.init(self.levels)
    self.run()
    self.status_save()
    if not self.params.interactive:
      sys.exit()
  
  # iterative updating phase
  def update (self):
    
    while True:
      
      # load status of MLMC simulation
      self.status_load()
      
      # wait for jobs to finish 
      self.join()
      
      # load results
      self.load()
      
      # compute and report error indicators
      self.indicators.compute (self.mcs)
      self.indicators.report  ()
      
      # compute and report errors
      self.config.samples.compute_errors ()
      self.config.samples.report_errors  ()
      
      if config.samples.finished ():
        break
      
      # compute estimated errors and required number of samples
      self.samples.update (self.levels, self.works, self.indicators)
      
      # report estimated errors and required number of samples
      self.samples.report ()
      
      # for interactive session, query user for additional input
      if self.params.interactive:
        self.user_query()
        self.samples.update(self.levels, self.works, self.indicators)
        self.samples.report()
      
      # compute additional samples
      self.run()
      
      # save status of MLMC simulation
      self.status_save()
      
      if not self.params.interactive:
        exit() 
  
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


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
import pickle

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
  
  def __init__ (self, id=1):
    vars (self) .update ( locals() )
  
  # used to set solver, discretizations, samples and balancer
  def set (self, name, value):
    vars (self) .update ( { name : value } )

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
    
    # determine finest level
    self.L = len(self.levels) - 1
    
    # setup required pairs of levels and types
    self.levels_types  = [ [level, self.FINE]   for level in self.levels      ]
    self.levels_types += [ [level, self.COARSE] for level in self.levels [1:] ]
    
    # indicators
    self.indicators = Indicators ( self.config.solver.indicator, self.levels, self.levels_types )
    
    # works
    # TODO: take into account _differences_ on all levels except the coarsest
    self.works = [ config.solver.work (discretization) for discretization in config.discretizations ]
    
    # core ratios
    self.ratios = [ config.solver.ratio (config.discretizations [self.L], discretization) for discretization in config.discretizations ]
    
    # setup samples
    self.config.samples.setup ( self.levels, self.works )
    
    # setup balancer
    self.config.balancer.setup (self.levels, self.levels_types, self.works, self.ratios )
    
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
    
    # initialize and validate the required number of samples
    self.config.samples.init     ()
    self.config.samples.validate ()
    
    # distribute initial samples
    self.config.balancer.distribute ()
    
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
        print
        print ' :: TOLERANCE reached.'
        self.status_save ()
        return
      
      # update, validate and report the required number of samples
      self.config.samples.update   ()
      self.config.samples.report   ()
      self.config.samples.validate ()
      
      # for interactive sessions, query user for additional input
      if self.params.query:
        while self.query():
          # check if the simulation is already finished 
          if self.config.samples.finished ():
            print
            print ' :: TOLERANCE reached.'
            self.status_save ()
            return
          # otherwise update the number of samples
          self.config.samples.update   ()
          self.config.samples.report   ()
          self.config.samples.validate ()
      
      # distribute additional samples
      self.config.balancer.distribute ()
      
      # compute additional samples
      self.run ()
      
      # save status of MLMC simulation
      self.status_save ()
      
      if not self.params.interactive:
        sys.exit () 
  
  # create MC objects
  def create_MCs (self, indices):
    self.mcs = []
    for i, (level, type) in enumerate(self.levels_types):
      self.mcs.append ( MC ( MC_Config (self.config, level, type, indices [level]), self.params, self.config.balancer.parallelizations [level] [type] ) )
  
  # run MC estimates
  def run (self):
    self.create_MCs (self.config.samples.indices.additional)
    print
    print ' :: SAMPLES TO COMPUTE:',
    print self.config.samples.counts.additional
    for mc in self.mcs:
      mc.validate ()
    for mc in self.mcs:
      mc.run ()
    self.config.samples.append ()
  
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
      print self.stats [ name ]
      for mc in self.mcs: 
        #if mc.config.type == self.FINE:   self.stats [ name ] += mc.stats [ name ]
        if mc.config.type == self.FINE:   iadd ( self.stats [ name ], mc.stats [ name ] )
        if mc.config.type == self.COARSE: self.stats [ name ] -= mc.stats [ name ]
    
    return self.stats
  
  # save MLMC status
  def status_save (self):
    
    statusf = open ( 'status.py', 'w' )
    pickle.dump ( self.config.samples.counts, statusf )
    statusf.close()
    print
    print (' :: INFO: MLMC status saved to status.py') 
    
  # laod MLMC status
  def status_load (self):
    
    statusf = open ( 'status.py', 'r' )
    self.config.samples.counts = pickle.load ( statusf )
    statusf.close()
    self.config.samples.make_indices ()
    print
    print (' :: INFO: MLMC status loaded from to status.py') 

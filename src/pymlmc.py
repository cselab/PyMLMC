
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
import subprocess

# === local imports

from MC import *
import helpers

sys.path.append ( os.path.dirname(__file__) + "/samples" )
sys.path.append ( os.path.dirname(__file__) + "/stats" )
sys.path.append ( os.path.dirname(__file__) + "/balancer" )

from samples  import *
from stats    import *
from balancer import *

# === classes

class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, config, params, run_id=1):
    
    # store configuration
    self.config = config
    self.params = params
    self.run_id = run_id
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1
    
    # determine levels
    self.levels = range ( len ( config ['discretizations'] ) )
    
    # setup required pairs of levels and types
    self.level_types  = [ [level, self.FINE]   for level in levels      ]
    self.level_types += [ [level, self.COARSE] for level in levels [1:] ]
    
    # list of MC objects
    mc = helpers.level_type_list (levels)
    
    # indicators
    #indicators = Indicators ( config ['solver'] .indicator )
    
    # MLMC results
    stats = {}
    
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
    self.config["samples"].init()
    self.run()
    self.status_save()
    if not self.params.interactive:
      exit()
  
  # iterative updating phase
  def update (self):
     
    while True:
      
      # load status of MLMC simulation
      self.status_load()
      
      # wait for jobs to finish 
      self.join()
      
      # load results
      self.load()
      
      # compute error indicators
      #self.indicators.compute (mc)
      
      #if self.indicators.error <= params.tol:
      if True:
        break
      
      # display estimated errors and required number of samples
      self.samples.update()
      
      if self.params.interactive:
        self.user_query()
        self.samples.update()
      
      # compute additional samples
      self.run()
      
      # save status of MLMC simulation
      self.status_save()
      
      if not self.params.interactive:
        exit() 

  # get MC configuration
  def get_mc_config (self, level, type):
    mc_config = {}
    mc_config ['level']   = level
    mc_config ['samples'] = self.config ['samples'] .indices [level]
    mc_config ['solver']  = self.config ['solver']
    mc_config ['discretization'] = self.config ['discretizations'] [level - type]
    mc_config ['type']           = type 
    return mc_config

  # create MC objects
  def create_MC (self):
    for level, type in self.levels_types:
      self.mc [level] [type] = MC ( get_mc_config (level, type), self.params, self.run_id )
   
  # run MC estimates
  def run (self):
    self.create_MC ()
    for level, type in self.levels_types:
      slef.mc [level] [type] .run ()
  
  # load the results from MC simulations
  def load (self):
    self.create_MC ()
    for level, type in self.levels_types:
      self.mc [level] [type] .load ()
  
  # assemble MC and MLMC estimates
  def assemble (self, stats):
    
    # assemble MC estimates
    for level, type in self.levels_types:
      self.mc [level] [type] .assemble (stats)
    
    # assemble MLMC estimates
    for name in [stat.name for stat in stats]:
      self.stats [ name ] = 0 
      for level, type in self.levels_types: 
        if type == self.FINE:   self.stats [ name ] += mc [level] [type] .stats [ name ]
        if type == self.COARSE: self.stats [ name ] -= mc [level] [type] .stats [ name ]
    
    return self.stats
  
  # load MLMC status
  def status_load (self):
    
    # TODO
  
  # save MLMC status
  def status_save (self):
    
    # TODO

if __name__ == "__main__":
  
  # parse input parameters
  # TODO
  params = []
  
  # configuration
  config = {}
  '''
  from solver_Cubism_MPCF import Cubism_MPCF
  config ['solver'] = Cubism_MPCF ()
  '''
  from solver_example import Example_solver
  config ['solver'] = Example_Solver ()
  
  N0 = 16
  L = 4
  config ['discretizations'] = grids_3d ( grids (16, 4) ]
  
  from samples_one_per_level import One_Per_Level
  config ['samples'] = One_Per_Level ()
  
  # create MLMC simulation
  mlmc = MLMC (config, params)
  
  # run MLMC simulation
  mlmc.simulation()
  
  # load simulation results
  mlmc.load()
  
  # statistics
  stats = [ Mean(), Variance() ]
  
  # assemble MLMC estimates
  mlmc.assemble (stats)
  
  # report results
  print mlmc.stats


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

from mc import *
import helpers

# === additional Python paths

sys.path.append ( os.path.dirname(__file__) + "/solver" )
sys.path.append ( os.path.dirname(__file__) + "/samples" )
sys.path.append ( os.path.dirname(__file__) + "/balancer" )
sys.path.append ( os.path.dirname(__file__) + "/stats" )

# === classes

class MLMC (object):
  
  # initialize MLMC
  # config must include solver, discretizations, and samples
  def __init__ (self, config, params, id=1):
    
    # store configuration
    self.config = config
    self.params = params
    self.id     = id
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1
    
    # determine levels
    self.levels = range ( len ( config ['discretizations'] ) )
    
    # setup required pairs of levels and types
    self.levels_types  = [ [level, self.FINE]   for level in self.levels      ]
    self.levels_types += [ [level, self.COARSE] for level in self.levels [1:] ]
    
    # list of MC objects
    self.mc = helpers.level_type_list (self.levels)
    
    # indicators
    #indicators = Indicators ( config ['solver'] .indicator )
    
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
    self.config["samples"].init(self.levels)
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
  
  # create MC objects
  def create_MC (self):
    for level, type in self.levels_types:
      mc_config = {}
      mc_config ['level']   = level
      mc_config ['samples'] = self.config ['samples'] .indices [level]
      mc_config ['solver']  = self.config ['solver']
      mc_config ['discretization'] = self.config ['discretizations'] [level - type]
      mc_config ['type']           = type
      self.mc [level] [type] = MC ( mc_config, self.params, self.id )
   
  # run MC estimates
  def run (self):
    self.create_MC ()
    for level, type in self.levels_types:
      self.mc [level] [type] .run ()
  
  # check if MC estimates are already available
  def join (self):
    self.create_MC ()
    for level, type in self.levels_types:
      if not self.mc [level] [type] .finished ():
        Exception ( ':: ERROR: MC simulations are not yet available')
  
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
   
   print (' :: WARNING: status_load() is not yet implemented.') 
    # TODO
  
  # save MLMC status
  def status_save (self):
    
    print (' :: WARNING: status_save() is not yet implemented.') 
    # TODO

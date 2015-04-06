
# # # # # # # # # # # # # # # # # # # # # # # # # #
# MLMC Config class
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

import helpers

# === additional Python paths

sys.path.append ( os.path.join (os.path.dirname(__file__), 'solver' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'samples' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'scheduler' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'stats' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'plot' ) )

# === default MLMC configuration

from solver_example    import Example_Solver
from samples_estimated import Estimated
from scheduler_static  import Static

# === classes

# configuration class for MLMC simulations

class MLMC_Config (object):
  
  # default configuration
  solver          = Example_Solver ()
  discretizations = helpers.grids_3d ( helpers.grids (1) )
  samples         = Estimated ()
  scheduler       = Static ()
  root            = '.'
  deterministic   = 0
  
  def __init__ (self, id=0):
    
    vars (self) .update ( locals() )
  
  # setup remaining variables
  def setup (self):
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1
    
    # determine levels
    self.levels = range ( len ( self.discretizations ) )
    
    # determine finest level
    self.L = len (self.levels) - 1
    
    # setup required pairs of levels and types
    levels_types_fine   = [ [level, self.FINE]   for level in self.levels [1:] ]
    levels_types_coarse = [ [level, self.COARSE] for level in self.levels [1:] ]
    self.levels_types   = [ [0, self.FINE] ]  + [ level_type for levels_types in zip (levels_types_coarse, levels_types_fine) for level_type in levels_types ]
    
    # works
    # TODO: take into account _differences_ on all levels except the coarsest
    self.works = [ self.solver.work (discretization) for discretization in self.discretizations ]
    
    # core ratios
    self.ratios = [ self.solver.ratio (self.discretizations [self.L], discretization) for discretization in self.discretizations ]

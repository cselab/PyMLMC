
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

import os
import sys

# === local imports

import helpers
import local
import numpy

# === additional Python paths

sys.path.append ( os.path.join (os.path.dirname(__file__), 'solver' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'samples' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'scheduler' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'stats' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'lib' ) )
sys.path.append ( os.path.join (os.path.dirname(__file__), 'plot' ) )

# === default MLMC configuration

from solver_Integral2D import Integral2D
from samples_estimated import Estimated
from scheduler_static  import Static

# === classes

# configuration class for MLMC simulations

class MLMC_Config (object):
  
  # default configuration
  solver          = Integral2D ()
  discretizations = helpers.grids (4)
  samples         = Estimated ()
  scheduler       = Static ()
  root            = '.'
  deterministic   = 0
  recycle         = 0
  inference       = 'correlations'
  degree          = 1
  iteration       = None
  
  def __init__ (self, id=0):
    
    vars (self) .update ( locals() )
  
  # setup remaining variables
  def setup (self):
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1

    # determine types
    if self.recycle:
      self.types  = lambda level : [self.FINE]
    else:
      self.types  = lambda level : [self.FINE, self.COARSE] if level > 0 else [self.FINE]

    # determine levels
    self.levels = range ( len ( self.discretizations ) )
    
    # determine finest level
    self.L = len (self.levels) - 1
    
    # setup required pairs of levels and types
    levels_types_fine   = [ [level, self.FINE]   for level in self.levels [1:] ]
    levels_types_coarse = [ [level, self.COARSE] for level in self.levels [1:] ]
    self.levels_types   = [ [0, self.FINE] ]  + [ level_type for levels_types in zip (levels_types_coarse, levels_types_fine) for level_type in levels_types ]

    # setup mapping of level and type to levels_types
    if self.recycle:
      self.pick = [ [0, None] ] + [ [level, level - 1] for level in self.levels [1:] ]
    else:
      self.pick = [ [0, None] ] + [ [2 * level, 2 * level - 1] for level in self.levels [1:] ]

    # works
    self.works = numpy.array ( [ self.solver.workunit * float ( self.solver.work (discretization) ) / local.performance for discretization in self.discretizations ] )

    # work ratios
    self.work_ratios = numpy.array ( [ self.works [level] / self.works [0] for level in self.levels ] )

    # default core ratios
    self.core_ratios = [ self.solver.ratio (discretization, self.discretizations [0]) for discretization in self.discretizations ]

  # report configuration
  def report (self):

    print
    print   ' :: CONFIGURATION:    '
    print   '  : MACHINE      :    %-30s' % local.name                         + '    ' + '[TYPE: %s]' % ('cluster'       if local.cluster      else 'standalone')
    print   '  : SOLVER       :    %-30s' % self.solver    .__class__.__name__ + '    ' + '[MODE: %s]' % ('deterministic' if self.deterministic else 'stochastic')
    if self.levels > 0 and not self.deterministic:
      print '                 |->  %-30s' % 'WORK RATIOS'                      + '    ' + '%s' % ' '.join ( [ helpers.intf (ratio) for ratio in self.work_ratios ] )
      print '                 |->  %-30s' % 'CORE RATIOS'                      + '    ' + '%s' % ' '.join ( [ helpers.intf (ratio) for ratio in self.core_ratios ] )
    print   '  : SAMPLES      :    %-30s' % self.samples   .__class__.__name__
    if not self.deterministic:
      print '  : SCHEDULER    :    %-30s' % self.scheduler .__class__.__name__
    print   '  : ROOT         :    %-30s' % self.root
    print   '  : RECYCLE      :    %-30s' % ( 'ENABLED' if self.recycle else 'DISABLED' )
    print   '  : INFERENCE    :    %-30s' % self.inference
    if self.inference:
      print '  : DEGREE       :    %-30s' % str (self.degree)

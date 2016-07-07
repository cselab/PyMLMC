
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Class for optimal coefficients for control variates
# TODO: add paper, description and link
# 
# Recycling disabled (default):
# Sukys, Rasthofer, Werelinger, Hadjidiukas, Rosinelli, Koumoutsakos
# "Uncertainty quantification in multi-phase cloud cavitation collapse flows using optimal control variate multi-level Monte Carlo sampling and petascale direct numerical simulations"
#
# Recycling  enabled:
# Peterstorfer, Willcox, Gunzburger
# "Optimal model management for multifidelity Monte Carlo estimation", 2015.
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import numpy

# === local imports

import helpers

# === classes

class Coefficients (object):
  
  def __init__ (self, levels, recycle):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L      = len (self.levels) - 1
    self.values = numpy.ones (self.L+1)

  # optimize coefficients of control variates given indicators
  # optimization can be performed for required specific sample-scaled indicators if sample numbers on each level are provided
  def optimize (self, indicators, samples=None):

    # no optimization if only one level is present
    if len (self.levels) == 1:
      return

    # === if recycling is enabled, coefficients can be computed explicitly

    if self.recycle:

      # each coefficient can be computed independently
      for level in self.levels [ : -1 ]:
        self.values [level] = indicators.correlation [level] * numpy.sqrt ( indicators.variance [self.L] [0] / indicators.variance [level] [0] )

    # === if recycling is disabled, coefficients are obtained by solving a linear system of equations

    else:
      
      # optimization problem as a linear system
      A = numpy.zeros ( [self.L, self.L] )
      b = numpy.zeros (self.L)

      # work-weighted optimization
      if samples == None:

        # assemble matrix from indicators
        for level in range (self.L):
          if level != 0:
            A [level] [level - 1] = - indicators.works [level] ** 2 * indicators.covariance [level]
          A [level] [level] = ( indicators.works [level] ** 2 + indicators.works [level + 1] ** 2 ) * indicators.variance [level] [0]
          if level != self.L - 1:
            A [level] [level + 1] = - indicators.works [level + 1] ** 2 * indicators.covariance [level + 1]
        
        # assemble right hand side
        b [-1] = indicators.works [self.L] ** 2 * indicators.covariance [self.L]
      
      # sample-weighted optimization
      else:

        # assemble matrix from indicators
        for level in range (self.L):
          if level != 0:
            A [level] [level - 1] = - indicators.covariance [level] / samples [level]
          A [level] [level] = indicators.variance [level] [0] / samples [level] + indicators.variance [level] [0] / samples [level + 1]
          if level != self.L - 1:
            A [level] [level + 1] = - indicators.covariance [level + 1] / samples [level + 1]

        # assemble right hand side
        b [-1] = indicators.covariance [self.L] / samples [self.L]

      # solve linear system
      print A
      print b
      self.values [ : -1 ] = numpy.linalg.solve (A, b)

    # if the result is 'fishy', revert to default values
    if numpy.isnan (self.values).any() or (self.values <= 0).any() or (self.values > 1).any():
      message = 'Fishy values of optimized coefficients - resetting all to 1.0'
      details = ' '.join ( [ helpers.scif (value) for value in self.values ] )
      helpers.warning (message, details=details)
      self.values = numpy.ones (self.L+1)

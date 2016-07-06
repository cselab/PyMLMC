
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Class for optimal coefficients for control variates
# TODO: add paper, description and link
# Recycling  enabled: Peterstorfer, Willcox, Gunzburger, "Optimal model management for multifidelity Monte Carlo estimation", 2015.
# Recycling disabled: TODO
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

      # if the result is 'fishy', revert to default values
      if numpy.isnan (self.values).any() or (self.values <= 0).any():
        self.values = numpy.ones (self.L+1)

    # === if recycling is disabled, coefficients are obtained by solving a linear system of equations

    else:

      # assemble matrix from indicators
      A = numpy.zeros ( [self.L, self.L] )
      for level in range (self.L):
        if level != 0:
          A [level] [level - 1] = - indicators.covariance [level]
          if samples != None:
            A [level] [level - 1] /= samples [level]
        A [level] [level] = indicators.variance [level] [0]
        if samples != None:
          A [level] [level] *= ( 1.0 / samples [level] + 1.0 / samples [level + 1] )
        else:
          A [level] [level] *= 2
        if level != self.L - 1:
          A [level] [level + 1] = - indicators.covariance [level + 1]
          if samples != None:
            A [level] [level + 1] /= samples [level + 1]

      # assemble right hand side
      b = numpy.zeros (self.L)
      b [-1] = indicators.covariance [self.L]
      if samples != None:
        b [-1] /= samples [self.L]

      # solve linear system
      self.values [ : -1 ] = numpy.linalg.solve (A, b)

    # if the result is 'fishy', revert to default values
    if numpy.isnan (self.values).any() or (self.values <= 0).any() or (self.values > 1).any():
      message = 'Fishy values of optimized coefficients - resetting all to 1.0'
      details = ' '.join ( [ helpers.scif (value) for value in self.values ] )
      helpers.warning (message, details=details)
      self.values = numpy.ones (self.L+1)


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
import os

# === local imports

import helpers

# === classes

class Coefficients (object):
  
  def __init__ (self, levels, recycle):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L      = len (self.levels) - 1
    self.values = numpy.ones (self.L+1)

    self.optimization = None

    self.coefficients_file = 'coefficients.dat'
    self.history = {}

  # compute cost functional
  def cost (self, indicators, factors):
    
    costs = numpy.zeros (self.L + 1)

    costs [ 0   ]  =     self.values [ 0      ] ** 2                   * indicators.variance [0] ['infered'] [0]
    costs [ 1 : ]  =     self.values [ 1 :    ] ** 2                   * indicators.variance [0] ['infered'] [ 1 : ]
    costs [ 1 : ] +=     self.values [   : -1 ] ** 2                   * indicators.variance [1] ['infered'] [ 1 : ]
    costs [ 1 : ] -= 2 * self.values [ 1 :    ] * self.values [ : -1 ] * indicators.covariance   ['infered'] [ 1 : ]

    costs *= factors
    
    return numpy.sum (costs)

  # optimize coefficients of control variates given indicators
  # optimization can be performed for required specific sample-scaled indicators if sample numbers on each level are provided
  def optimize (self, indicators, samples=[]):

    # no optimization if only one level is present
    if len (self.levels) == 1:
      return

    # a-priori (work-weighted) optimization
    if samples == []:
      pairworks = indicators.pairworks / indicators.pairworks [0]
      factors = numpy.array (pairworks)

    # a-posteriori (sample-weighted) optimization
    else:
      factors = 1.0 / numpy.maximum ( 1, numpy.array (samples) )

    # cost of plain (non-optimized) estimator
    cost_plain = self.cost (indicators, factors)

    # === if recycling is enabled, coefficients can be computed explicitly

    if self.recycle:

      # each coefficient can be computed independently
      for level in self.levels [ : -1 ]:
        self.values [level] = indicators.correlation ['infered'] [level] * numpy.sqrt ( indicators.variance [0] ['infered'] [self.L] / indicators.variance [0] ['infered'] [level] )
    
    # === if recycling is disabled, coefficients are obtained by solving a linear system of equations

    else:
      
      # optimization problem as a linear system
      A = numpy.zeros ( [self.L, self.L] )
      b = numpy.zeros (self.L)

      # assemble matrix from indicators
      for level in range (self.L):
        if level != 0:
          A [level] [level - 1] = - factors [level] * indicators.covariance ['infered'] [level]
        A [level] [level]  = factors [level    ] * indicators.variance [0]  ['infered'] [level    ]
        A [level] [level] += factors [level + 1] * indicators.variance [1]  ['infered'] [level + 1]
        if level != self.L - 1:
          A [level] [level + 1] = - factors [level + 1] ** 2 * indicators.covariance ['infered'] [level + 1]
      
      # assemble right hand side
      b [-1] = factors [self.L] * indicators.covariance ['infered'] [self.L]
      
      # solve linear system
      self.values [ : -1 ] = numpy.linalg.solve (A, b)

    # cost of OCV estimator
    cost_ocv = self.cost (indicators, factors)

    # compute optimization factor
    self.optimization = cost_plain / cost_ocv

    '''
    # if the result is 'fishy', revert to default values
    if self.optimization < 1 or numpy.isnan (self.values).any() or (self.values > 10).any() or (self.values < -10).any():
      message = 'Invalid values of optimized coefficients or failed optimization - resetting all to 1.0'
      details = ' '.join ( [ helpers.scif (value) for value in self.values ] ) + ', optimization = %.2f' % self.optimization
      helpers.warning (message, details=details)
      self.values = numpy.ones (self.L+1)
      self.optimization = None
    '''

  # save coefficients
  def save (self, iteration):

    # initialize history
    self.history [iteration] = self.values

    # dump history
    helpers.delete (self.coefficients_file)
    for iteration in range (iteration + 1):
      helpers.dump (self.history [iteration], '%f', 'coefficients', self.coefficients_file, iteration)

  # load coefficients
  def load (self, config):
    
    self.history = {}
    path = os.path.join (config.root, self.coefficients_file)
    if os.path.exists (path):
      execfile ( path, globals(), self.history )



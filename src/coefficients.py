
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Class for optimal coefficients for control variates
# TODO: add paper, description and link
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
  
  def __init__ (self, levels, ):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L      = len (self.levels) - 1
    self.values = numpy.ones (self.L+1)

  # optimize coefficients of control variates given indicators
  # optimization can be performed for required specific sample-scaled indicators if sample numbers on each level are provided
  def optimize (self, indicators, samples=None):

    if len (self.levels) == 0:
      self.values = numpy.array ( [1.0] )
      return

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

    # simpler solution
    #self.values =

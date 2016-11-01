
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Shells for the Cubism-MPCF cloud collapse simulations
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
import copy, os

from dataclass_series import *

class Shells (Series):

  name       = 'shells'
  dimensions = 2

  def __init__ (self, qois, filename='statistics.dat', metaqois=['step', 't'], uid='t', span=[0,1], sampling=1000, ranges=None, count=1, extent=[0,1]):

    # save configuration
    vars (self) .update ( locals() )

    self.meta = {}
    self.data = {}

  def load (self, directory, verbosity):

    # create a copy of this class or results
    results = copy.deepcopy (self)

    # get results for a Series dataclass
    series = copy.deepcopy (self)
    series = super (Shells, series)
    series.qois = []
    for qoi in results.qois:
      for shell in xrange (results.count):
        series.qois.append ('%s_shell_avg%d' % (qoi, shell + 1))
    series.load (directory, verbosity)
    
    # copy meta data from Series dataclass
    results.meta = copy.deepcopy (series.meta)

    # merge shells
    shape = (results.sampling, results.count)
    for qoi in results.qois:
      results.data [qoi] = numpy.empty (shape, dtype=float)
      for shell in xrange (results.count):
        results.data [qoi] [ : , shell ] = series.data [ '%s_shell_avg%d' % (qoi, shell + 1) ] [:]

    # additional meta data
    results.meta ['xrange'] = results.span
    results.meta ['yrange'] = results.extent
    results.meta ['xlabel'] = 'time'
    results.meta ['ylabel'] = 'distance'
    results.meta ['xunit']  = r'$\mu s$'
    results.meta ['yunit']  = r'$mm$'

    return results

  # serialized access to data
  def serialize (self, qoi):

    shape    = self.data [qoi] .shape
    elements = shape [0] * shape [1]
    size     = numpy.prod (shape) / elements
    return self.data [qoi] .reshape ( (elements, size) )

  def resize (self, size):

    for key in self.data.keys():
      shape = self.data [key] .shape
      if size > 1:
        shape += tuple([size])
      self.data [key] = numpy.empty (shape)
      self.data [key] .fill (float ('nan'))

  def __str__ (self):

    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output

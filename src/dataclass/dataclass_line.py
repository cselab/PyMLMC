
# # # # # # # # # # # # # # # # # # # # # # # # # #
# 1-D line of multi-dimensional array-valued fields
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
import h5py
import copy, os
import linecache

from dataclass_slice import *

class Line (Slice):

  name       = 'line'
  dimensions = 1

  def __init__ (self, qois=None, slices=1, dump=1, line=0.5, ranges=None, extent=[0,1]):
    
    # save configuration
    vars (self) .update ( locals() )
    
    self.filename = 'data_%06d-%s_slice%d.h5'
    self.qoinames = { 'p' : 'pressure', 'a' : 'alpha', 'r' : 'density' }
    self.logsfile  = 'dump.log'

    self.meta = {}
    self.data = {}
  
  def load (self, directory, verbosity):

    # create a copy of this class
    results = copy.deepcopy (self)

    # load slices
    slices = Slice.load (self, directory, verbosity)

    # compute the required index for the line
    index = int ( self.line * slices.meta ['NY'] )

    # pick the specified line only for all qois
    for qoi in self.qois:
      results.data [qoi] = slices.data [qoi] [:, index]

    # load meta data
    results.meta = copy.deepcopy (slices.meta)
    results.meta ['shape'] = len (results.data [qoi])

    return results
  
  # serialized access to data
  def serialize (self, qoi):
    return self.data [qoi]
  
  # returns data for a requested qoi
  def __getitem__ (self, qoi):
    return self.data [qoi]
  
  # stores data for a requested qoi
  def __setitem__ (self, qoi, data):
    self.data [qoi] = data
  
  def init (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = numpy.zeros (a.meta ['shape'])

  def resize (self, size):

    for key in self.data.keys():
      shape = self.data [key] .shape
      if size > 1:
        shape += tuple([size])
      self.data [key] = numpy.empty (shape)
      self.data [key] .fill (float ('nan'))

  def clip (self, range=None):

    if range:
      (lower, upper) = range
      for key in self.data.keys():
        if lower != None:
          self.data [key] = numpy.maximum ( lower, self.data [key] )
        if upper != None:
          self.data [key] = numpy.minimum ( upper, self.data [key] )

    if self.ranges and not range:
      for key in self.data.keys():
        for qoi, (lower, upper) in self.ranges.iteritems():
          if qoi in key:
            if lower != None:
              self.data [key] = numpy.maximum ( lower, self.data [key] )
            if upper != None:
              self.data [key] = numpy.minimum ( upper, self.data [key] )
  
  def __rmul__ (self, a):
    for key in self.data.keys():
      self.data [key] *= a
    return self

  def __iadd__ (self, a):

    if not self.data:
      self.init (a)

    if self.meta ['shape'] == a.meta ['shape']:

      for key in self.data.keys():
        self.data [key] += a.data [key]

    if self.meta ['shape'] > a.meta ['shape']:

      factor = self.meta ['shape'] / a.meta ['shape']

      for key in self.data.keys():
        self.data [key] += numpy.squeeze ( numpy.kron ( a.data [key], numpy.ones ((1, factor)) ) )

    elif self.meta ['shape'] < a.meta ['shape']:

      factor = a.meta ['shape'] / self.meta ['shape']

      for key in self.data.keys():
        self.data [key] = numpy.squeeze ( numpy.kron ( self.data [key], numpy.ones ((1, factor)) ) ) + a.data [key]
      
      self.meta = copy.deepcopy (a.meta)

    return self
  
  def __isub__ (self, a):
    return self += (-1) * a
  
  '''
  def __str__ (self):
    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output
  '''

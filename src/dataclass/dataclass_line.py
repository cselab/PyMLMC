
# # # # # # # # # # # # # # # # # # # # # # # # # #
# 1-D line of multi-dimensional array-valued fields
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
from scipy import signal
import h5py
import copy, os
import linecache

from dataclass_slice import *

class Line (Slice):

  name       = 'line'
  dimensions = 1

  def __init__ (self, qois=None, slices=1, dump=1, line=0.5, ranges=None, extent=[0,1], picker=None, eps=None):
    
    # save configuration
    vars (self) .update ( locals() )
    self.extent = copy.deepcopy (extent)
    
    self.filename = 'data_%06d-%s_slice%d.h5'
    self.qoinames = { 'p' : 'pressure', 'a' : 'alpha', 'r' : 'density' }
    self.logsfile  = 'dump.log'

    self.meta = {}
    self.data = {}
  
  def load (self, directory, verbosity):

    # create a copy of this class
    results = copy.deepcopy (self)

    # if picker is specified, get the dump
    if self.picker != None:
      self.dump = self.picker.pick (directory, verbosity)

    # read dump log
    step, time = self.read_dump (directory)

    # load all qois
    for qoi in self.qois:

      # single slices are loaded normally
      if not hasattr (self.slices, '__iter__'):
        filename = self.filename % ( step, self.qoinames [qoi], self.slices )
        with h5py.File ( os.path.join (directory, filename), 'r' ) as f:
          index = int ( self.line * f ['data'] .shape [1] )
          results.data [qoi] = f ['data'] [:, index]

      # for multiple specified files, compute arithmetic average
      else:
        filename = self.filename % ( step, self.qoinames [qoi], self.slices [0] )
        with h5py.File ( os.path.join (directory, filename), 'r' ) as f:
          index = int ( self.line * f ['data'] .shape [1] )
          results.data [qoi] = f ['data'] [:, index]
        for slice in self.slices [1:]:
          filename = self.filename % ( step, self.qoinames [qoi], slice )
          with h5py.File ( os.path.join (directory, filename), 'r' ) as f:
            index = int ( self.line * f ['data'] .shape [1] )
            results.data [qoi] += f ['data'] [:, index]
      results.data [qoi] /= len (self.slices)

      # remove trivial dimensions
      results.data [qoi] = numpy.squeeze (results.data [qoi])

    # compute magnitude of vector-valued elements
    if results.data [qoi] .ndim > 1:
      results.data [qoi] = numpy.linalg.norm (results.data [qoi], norm=2, axis=1)

    # smoothen data
    if self.eps != None:
      for qoi in self.qois:
        results.smoothen (qoi, self.eps)

    # load meta data
    results.meta = {}
    results.meta ['step'] = step
    results.meta ['t'] = time
    results.meta ['NX'] = len ( results.data [qoi] )
    results.meta ['shape'] = results.meta ['NX']
    results.meta ['xlabel'] = 'x'
    results.meta ['xrange'] = results.extent
    results.meta ['xunit'] = r'$mm$'
    dx = float ( numpy.diff (results.meta ['xrange']) ) / results.meta ['NX']
    results.meta ['x'] = numpy.linspace (results.meta ['xrange'] [0] + 0.5 * dx, results.meta ['xrange'] [1] - 0.5 * dx, results.meta ['NX'] )

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

  def smoothen (self, qoi, eps):

    length  = len (self [qoi])
    width   = length * eps / (self.extent [1] - self.extent [0])
    kernel  = signal.gaussian (length, width)

    self [qoi] = signal.fftconvolve (self [qoi], kernel, mode='same')

  def __rmul__ (self, a):
    result = copy.deepcopy (self)
    for key in result.data.keys():
      result.data [key] *= a
    return result

  def __lmul__ (self, a):
    return self * a

  def inplace (self, a, action):

    if not self.data:
      self.init (a)

    if self.meta ['shape'] == a.meta ['shape']:

      for key in self.data.keys():
        getattr (self.data [key], action) (a.data [key])

    if self.meta ['shape'] > a.meta ['shape']:

      factor = self.meta ['shape'] / a.meta ['shape']

      for key in self.data.keys():
        #self.data [key] .__dict__ [action] ( numpy.squeeze ( numpy.kron ( a.data [key], numpy.ones ((1, factor)) ) ) )
        getattr (self.data [key], action) ( numpy.squeeze ( numpy.kron ( a.data [key], numpy.ones ((1, factor)) ) ) )

    elif self.meta ['shape'] < a.meta ['shape']:

      factor = a.meta ['shape'] / self.meta ['shape']

      for key in self.data.keys():
        self.data [key] = numpy.squeeze ( numpy.kron ( self.data [key], numpy.ones ((1, factor)) ) )
        getattr (self.data [key], action) (a.data [key])
      
      self.meta = copy.deepcopy (a.meta)

    return self
  
  def __iadd__ (self, a):
    return self.inplace (a, '__iadd__')

  def __isub__ (self, a):
    return self.inplace (a, '__isub__')
  
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

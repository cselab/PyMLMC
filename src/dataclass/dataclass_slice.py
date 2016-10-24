
# # # # # # # # # # # # # # # # # # # # # # # # # #
# 2-D slices of multi-dimensional array-valued fields
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

class Slice (object):

  name       = 'slice'
  dimensions = 2

  def __init__ (self, qois=None, slices=1, dump=1, ranges=None, extent=[0,1]):
    
    # save configuration
    vars (self) .update ( locals() )
    
    self.filename = 'data_%06d-%s_slice%d.h5'
    self.qoinames = { 'p' : 'pressure', 'a' : 'alpha', 'm' : 'velocity', 'r' : 'density' }
    self.logsfile  = 'dump.log'

    self.meta = {}
    self.data = {}
  
  def load (self, directory, verbosity):

    # create a copy of this class
    results = copy.deepcopy (self)

    # read dump log
    line = linecache.getline (os.path.join ( directory, self.logsfile ), self.dump)
    linecache.clearcache ()
    entries = line.strip().split()
    step = int   ( entries [1] .split('=') [1] )
    time = float ( entries [2] .split('=') [1] )

    # load all qois
    for qoi in self.qois:

      # single slices are loaded normally
      if not hasattr (self.slices, '__iter__'):
        filename = self.filename % ( step, self.qoinames [qoi], self.slices )
        with h5py.File ( os.path.join (directory, filename), 'r' ) as f:
          results.data [qoi] = numpy.array ( f.get ('data') )
      
      # for multiple specified files, compute arithmetic average
      else:
        filename = self.filename % ( step, self.qoinames [qoi], self.slices [0] )
        with h5py.File ( os.path.join (directory, filename), 'r' ) as f:
          results.data [qoi] = numpy.array ( f.get ('data') )
        for slice in self.slices [1:]:
          filename = self.filename % ( step, self.qoinames [qoi], slice )
          with h5py.File ( os.path.join (directory, filename), 'r' ) as f:
            results.data [qoi] += numpy.array ( f.get ('data') )
        results.data [qoi] /= len (self.slices)
      
      # remove trivial dimensions
      results.data [qoi] = numpy.squeeze (results.data [qoi])

      # compute magnitude of vector-valued elements
      if results.data [qoi] .ndim > 2:
        results.data [qoi] = numpy.linalg.norm (results.data [qoi], norm=2, axis=2)
    
    # load meta data
    results.meta = {}
    results.meta ['step'] = step
    results.meta ['t'] = time
    results.meta ['NX'] = results.data [qoi] .shape [0]
    results.meta ['NY'] = results.data [qoi] .shape [1]
    results.meta ['shape'] = results.data [qoi] .shape
    results.meta ['xlabel'] = 'x'
    results.meta ['ylabel'] = 'y'
    results.meta ['xrange'] = results.extent
    results.meta ['yrange'] = results.extent
    results.meta ['xunit'] = r'$mm$'
    results.meta ['yunit'] = r'$mm$'
    dx = float ( numpy.diff (results.meta ['xrange']) ) / results.meta ['NX']
    dy = float ( numpy.diff (results.meta ['yrange']) ) / results.meta ['NY']
    results.meta ['x'] = numpy.linspace (results.meta ['xrange'] [0] + 0.5 * dx, results.meta ['xrange'] [1] - 0.5 * dx, results.meta ['NX'] )
    results.meta ['y'] = numpy.linspace (results.meta ['yrange'] [0] + 0.5 * dy, results.meta ['yrange'] [1] - 0.5 * dy, results.meta ['NY'] )

    return results
  
  # serialized access to data
  def serialize (self, qoi):

    shape    = self.data [qoi] .shape
    elements = shape [0] * shape [1]
    size     = numpy.prod (shape) / elements
    return self.data [qoi] .reshape ( (elements, size) )
  
  # returns data for a requested qoi
  def __getitem__ (self, qoi):
    return self.data [qoi]
  
  # stores data for a requested qoi
  def __setitem__ (self, qoi, data):
    self.data [qoi] = data

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

  # check if the loaded result is invalid
  def invalid (self):

    for result in self.data.values():
      if numpy.isnan (result) .any() or numpy.isinf (result) .any():
        return 1

    return 0

  def __rmul__ (self, a):
    result = copy.deepcopy (self)
    for key in result.data.keys():
      result.data [key] *= a
    return result

  def __lmul__ (self, a):
    return self * a

  def inplace (self, a, action):

    if self.meta ['shape'] == a.meta ['shape']:

      for key in self.data.keys():
        getattr (self.data [key], action) (a.data [key])

    if self.meta ['shape'] [0] > a.meta ['shape'] [0] and self.meta ['shape'] [1] > a.meta ['shape'] [1]:

      xfactor = self.meta ['shape'] [0] / a.meta ['shape'] [0]
      yfactor = self.meta ['shape'] [1] / a.meta ['shape'] [1]

      for key in self.data.keys():
        getattr (self.data [key], action) ( numpy.kron ( a.data [key], numpy.ones ((xfactor, yfactor)) ) )

    elif self.meta ['shape'] [0] < a.meta ['shape'] [0] and self.meta ['shape'] [1] < a.meta ['shape'] [1]:

      xfactor = a.meta ['shape'] [0] / self.meta ['shape'] [0]
      yfactor = a.meta ['shape'] [1] / self.meta ['shape'] [1]

      for key in self.data.keys():
        self.data [key] = numpy.kron ( self.data [key], numpy.ones ((xfactor, yfactor)) )
        getattr (self.data [key], action) (a.data [key])

      self.meta = copy.deepcopy (a.meta)

    else:
      print
      print ' :: ERROR [Slice.iadd]: shapes of arrays are incompatible.'
      print
      return None

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

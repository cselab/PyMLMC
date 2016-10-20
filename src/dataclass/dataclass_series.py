
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Container for various data classes used in solvers
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
import copy, os

class Series (object):

  name       = 'series'
  dimensions = 1

  def __init__ (self, filename='statistics.dat', split=('step', 't'), uid='t', span=[0,1], sampling=1000, ranges=None):

    # save configuration
    vars (self) .update ( locals() )

    self.meta = {}
    self.data = {}

  def load (self, directory, verbosity):
    
    results = copy.deepcopy (self)

    outputfile = open ( os.path.join (directory, self.filename), 'r' )
    
    data = numpy.genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # split metadata from actual data
    for key in self.split:
      results.meta [key] = records [key]
      del records [key]
    results.data = records

    # filter out duplicate entries and then sort results
    if results.uid != None:
      results.unique ()
      results.sort   ()

    # interpolate results
    if results.sampling != None:
      results.interpolate ()

    # additional meta data
    results.meta ['xrange'] = results.span
    results.meta ['xlabel'] = 'time'
    results.meta ['xunit']  = r'$\mu s$'
    results.meta ['x']      = results.meta ['t']

    return results

  # returns data for a requested qoi
  def __getitem__ (self, qoi):
    return self.data [qoi]

  # stores data for a requested qoi
  def __setitem__ (self, qoi, data):
    self.data [qoi] = data

  # serialized access to data
  def serialize (self, qoi):
    return self.data [qoi]

  '''
  def append (self, filename, meta_keys):
    
    outputfile = open ( filename, 'r' )
    
    data = numpy.genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # filter out existing entries
    
    positions = []
    for position, step in enumerate (records ['step']):
      if step in self.meta ['step']:
        positions .append (position)
    for key in records.keys():
      records [key] = numpy.delete ( records [key], positions )
    
    # split metadata from actual data
    
    meta = {}
    for key in meta_keys:
      meta [key] = records [key]
      del records [key]
    
    # array of NaN's for filling the gaps
    
    count = len (records.values()[0])
    nan_array = numpy.empty ( (count, 1) )
    nan_array [:] = numpy.NAN
    
    # append metadata
    
    for key in meta.keys():
      if key in self.meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], meta [key] )
    
    # append data
    
    for key in records.keys():
      if key in self.data.keys():
        self.data [key] = numpy.append ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], nan_array )

    # fill in remaining data

    for key in self.data.keys():
      if key not in records.keys():
        self.data [key] = numpy.append ( self.data [key], nan_array )
  
  def load_v1 (self, filename, meta_keys, data_keys, meta_formats, data_formats):
    
    outputfile = open ( filename, 'r' )
    
    data = numpy.loadtxt ( outputfile, dtype = { 'names' : meta_keys + data_keys, 'formats' : meta_formats + data_formats } )
    records = dict ( (key, data [key]) for key in meta_keys + data_keys )
    
    outputfile.close()
    
    # split metadata from actual data
    
    for key in meta_keys:
      self.meta [key] = records [key]
      del records [key]
    self.data = records
  
  def append_v1 (self, filename, meta_keys, data_keys, meta_formats, data_formats):
    
    outputfile = open ( filename, 'r' )
    
    from numpy import loadtxt
    data = loadtxt ( outputfile, dtype = { 'names' : meta_keys + data_keys, 'formats' : meta_formats + data_formats } )
    records = dict ( (key, data [key]) for key in meta_keys + data_keys )
    
    outputfile.close()
    
    # filter out existing entries
    
    positions = []
    for position, step in enumerate (records ['step']):
      if step in self.meta ['step']:
        positions .append (position)
    for key in records.keys():
      records [key] = numpy.delete ( records [key], positions )
    
    # kinetic energy fix
    #extent = 20
    #extent = 40
    #records ['ke_avg'] /= float (extent) ** 3
    #records ['ke_avg'] *= 61
    #records ['ke_avg'] *= 344
    
    # array of NaN's for filling the gaps
    
    count = len (records.values() [0])
    nan_array = numpy.empty ( (count, 1) )
    nan_array [:] = numpy.NAN
    
    # append metadata
    
    for key in meta_keys:
      if key in self.meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], records [key] )
    
    # append data
    
    for key in data_keys:
      if key in self.data.keys():
        self.data [key] = numpy.append ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta_keys:
        self.meta [key] = numpy.append ( self.meta [key], nan_array )
    
    # fill in remaining data
    
    for key in self.data.keys():
      if key not in data_keys:
        self.data [key] = numpy.append ( self.data [key], nan_array )
  
  def append_v2 (self, filename, meta_keys):

    outputfile = open ( filename, 'r' )

    data = numpy.genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # filter out existing entries
    
    positions = []
    for position, step in enumerate (records ['step']):
      if step in self.meta ['step']:
        positions .append (position)
    for key in records.keys():
      records [key] = numpy.delete ( records [key], positions )
    
    # split metadata from actual data
    
    meta = {}
    for key in meta_keys:
      meta [key] = records [key]
      del records [key]
    
    # array of NaN's for filling the gaps
    
    count = len (records.values()[0])
    nan_array = numpy.empty ( (count, 1) )
    nan_array [:] = numpy.NAN
    
    # append metadata
    
    for key in meta.keys():
      if key in self.meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], meta [key] )
    
    # append data
    
    for key in records.keys():
      if key in self.data.keys():
        self.data [key] = numpy.append ( self.data [key], records [key] )
  
    # fill in remaining metadata
    
    for key in self.meta.keys():
      if key not in meta.keys():
        self.meta [key] = numpy.append ( self.meta [key], nan_array )

    # fill in remaining data

    for key in self.data.keys():
      if key not in records.keys():
        self.data [key] = numpy.append ( self.data [key], nan_array )
  '''

  # filter out duplicate entries (keep the first occurrence only)
  def unique (self):
    
    # obtain positions of duplicate entries
    positions = []
    values    = []
    for position, value in enumerate (self.meta [self.uid]):
      if value in values:
        positions .append (position)
      else:
        values .append (value)
    
    # remove duplicate entries from metadata
    for key in self.meta.keys():
      self.meta [key] = numpy.delete ( self.meta [key], positions )
    
    # remove duplicate entries from data
    for key in self.data.keys():
      self.data [key] = numpy.delete ( self.data [key], positions )
  
  def sort (self):
    
    # obtain sorting order
    order = numpy.argsort (self.meta [self.uid])
    
    # sort metadata
    for key in self.meta.keys():
      self.meta [key] = self.meta [key] [order]
    
    # sort data
    for key in self.data.keys():
      self.data [key] = self.data [key] [order]
  
  def interpolate (self):

    begin = self.span [0]
    end   = self.span [1]

    if begin == None: begin = self.meta [self.uid] [0]
    if end   == None: end   = self.meta [self.uid] [-1]
    
    leftnan  = numpy.abs (begin - self.meta [self.uid] [0] ) > 0.01 * numpy.abs (end - begin)
    rightnan = numpy.abs (end   - self.meta [self.uid] [-1]) > 0.01 * numpy.abs (end - begin)
    
    times = numpy.linspace ( begin, end, self.sampling )
    for key in self.data.keys():
      if leftnan:
        left = float ('nan')
      else:
        left = self.data [key] [0]
      if rightnan:
        right = float ('nan')
      else:
        right = self.data [key] [-1]
      self.data [key] = numpy.interp ( times, self.meta [self.uid], self.data [key], left=left, right=right )
    
    self.meta [self.uid] = times
  
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

  def init (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = numpy.zeros ( len ( a.data [key] ) )

  def resize (self, size):

    for key in self.data.keys():
      shape = self.data [key] .shape
      if size > 1:
        shape += tuple([size])
      self.data [key] = numpy.empty (shape)
      self.data [key] .fill (float ('nan'))

  def __rmul__ (self, a):
    result = copy.deepcopy (self)
    for key in result.data.keys():
      result.data [key] *= a
    return result

  def __lmul__ (self, a):
    return self * a
    
  def __iadd__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      self.data [key] += a.data [key]
    return self
  
  def __isub__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      self.data [key] -= a.data [key]
    return self
  
  def __str__ (self):
    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Container for various data classes used in solvers
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy

class Interpolated_Time_Series (object):
  
  def __init__ (self):
    
    # somehow this is needed here --
    # otherwise I get non-empty dictionaries upon instantiation
    self.meta = {}
    self.data = {}
  
  def load (self, filename, meta_keys):
    
    outputfile = open ( filename, 'r' )
    
    data = numpy.genfromtxt ( outputfile, names = True, delimiter = ' ', dtype = None )
    records = dict ( (key, data [key]) for key in data.dtype.names )
    
    outputfile.close()
    
    # split metadata from actual data
    
    for key in meta_keys:
      self.meta [key] = records [key]
      del records [key]
    self.data = records
  
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
  
  # filter out duplicate entries (keep the first occurrence only)
  def unique (self, key):
    
    # obtain positions of duplicate entries
    positions = []
    values    = []
    for position, value in enumerate (self.meta ['step']):
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
  
  def sort (self, key):
    
    # obtain sorting order
    order = numpy.argsort (self.meta [key])

    # sort metadata
    for key in self.meta.keys():
      self.meta [key] = self.meta [key] [order]
    
    # sort data
    for key in self.data.keys():
      self.data [key] = self.data [key] [order]

  def interpolate (self, points, begin=None, end=None):
    
    if begin == None: begin = self.meta ['t'] [0]
    if end   == None: end   = self.meta ['t'] [-1]
    
    times = numpy.linspace ( begin, end, points )
    for key in self.data.keys():
      self.data [key] = numpy.interp ( times, self.meta ['t'], self.data [key], left=float('nan'), right=float('nan') )
    
    self.meta ['t']  = times
  
  def init (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = []
      for step in xrange ( len ( a.data [key] ) ):
        self.data [key] .append ( 0 )
  
  def __iadd__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] += a.data [key] [step]
    return self
  
  def __isub__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] -= a.data [key] [step]
    return self
  
  def __str__ (self):
    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output
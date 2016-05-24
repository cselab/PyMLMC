
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Container for various data classes used in solvers
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
from PIL import Image

# dataclass for loading snapshots of the multi-dimensional array-valued fields,
# e.g. cell values of a (possibly sliced) computational domain
class Domain_Snapshot (object):
  
  def __init__ (self):
    
    # somehow this is needed here --
    # otherwise I get non-empty dictionaries upon instantiation
    self.meta = {}
    self.data = {}
  
  def load (self, filename, resize=None):

    # get meta information
    # TODO: parse step and time?
    self.meta ['t'] = ['']

    # open images
    # TODO: reduce number of channels to a single one (no need for RGBA) - also, would be good to increase _resolution_
    image = Image.open(filename).convert ('RGBA')

    # resize, if needed
    if resize:
      image = image.resize (resize)

    # load data into numpy array
    self.data [filename] = [ numpy.array (image, dtype=float) ]

  def init (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = [ numpy.zeros (a.data [key] [step] .shape ) for step in xrange ( len ( a.data [key] ) ) ]

  def __rmul__ (self, a):
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] *= a
    return self

  def __iadd__ (self, a):
    if not self.data:
      self.init (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        # TODO: this needs to be fixed for nested arrays
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


# # # # # # # # # # # # # # # # # # # # # # # # # #
# General samples classes
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers

import os
import numpy

class Counts (object):

  optimal    = []
  computed   = []
  additional = []
  combined   = []

  loaded     = []
  failed     = []
  invalid    = []

  def __init__ (self, levels, tolerate):

    self.levels   = levels
    self.tolerate = tolerate

  def available (self):

    if self.tolerate:
      return self.loaded
    else:
      return self.computed

  def report (self, available):

    print '  :'
    print '  :   LEVEL    : ' + ' '.join ( [ helpers.intf (level, table=1)       for level in self.levels ] )
    print '  :--------------' + '-'.join ( [ helpers.intf (None, table=1, bar=1) for level in self.levels ] )
    
    print '  : Computed   :',
    for level in self.levels:
      print helpers.intf (self.available() [level], table=1),
    print

    if available:

      print '  : Optimal    :',
      for level in self.levels:
        print helpers.intf (self.optimal [level], table=1),
      print

      print '  : Updated    :',
      for level in self.levels:
        print helpers.intf (self.available() [level] + self.additional [level], table=1),
      print

      print '  : Additional :',
      for level in self.levels:
        print helpers.intf (self.additional [level], table=1),
      print

class Indices (object):
  
  computed   = []
  additional = []
  combined   = []
  
  loaded     = []
  failed     = []
  invalid    = []
  
  def make (self, counts):
    
    self.computed   = [ range ( 0,                       counts.computed [level] ) for level in range(len(counts.computed)) ]
    self.additional = [ range ( counts.computed [level], counts.computed [level] + counts.additional [level] ) for level in range(len(counts.additional)) ]
    self.combined   = [ range ( 0,                       counts.combined [level] ) for level in range(len(counts.combined)) ]

class Samples (object):
  
  samples_file = 'samples.dat'
  available    = 0
  history      = {}
  
  def setup (self, levels, works, tolerate, recycle):
    
    # store configuration
    vars (self) .update ( locals() )
    
    # if recycling is disabled, a 'sample' is considered to be a pair of fine and coarse samples
    self.pairworks = numpy.array (works)
    if not self.recycle:
      self.pairworks [ 1 : ] += works [ : -1 ]

    self.counts  = Counts (levels, tolerate)
    self.indices = Indices ()
    
    self.L = len(levels) - 1

    self.counts.computed   = numpy.zeros (self.L + 1, dtype=int)
    self.counts.optimal    = numpy.zeros (self.L + 1, dtype=int)
    self.counts.additional = numpy.zeros (self.L + 1, dtype=int)

    self.counts.loaded   = numpy.zeros (self.L + 1, dtype=int)
    self.counts.failed   = numpy.zeros (self.L + 1, dtype=int)
    self.counts.invalid  = numpy.zeros (self.L + 1, dtype=int)

    self.indices.loaded  = [ None for level in self.levels ]
    self.indices.failed  = [ None for level in self.levels ]
    self.indices.invalid = [ None for level in self.levels ]

    self.tolerate = 0
  
  def validate (self):
    
    for level in self.levels:
      if self.counts.additional [level] < 0:
        Exception (" :: ERROR: Encountered a level with negative number of samples: counts.updated [%d] = %d" % (level, self.counts.additional [level]) )

  def save (self, iteration):

    # initialize history
    if len (self.history) == 0:
      self.history ['computed']   = {}
      self.history ['additional'] = {}
      self.history ['combined']   = {}

    # append history
    self.history ['computed']   [iteration] = self.counts.computed
    self.history ['additional'] [iteration] = self.counts.additional
    self.history ['combined']   [iteration] = self.counts.combined
    
    # dump history
    helpers.delete (self.samples_file)
    for i in range (iteration + 1):
      for entry in self.history:
        helpers.dump (self.history [entry] [i], '%d', entry, self.samples_file, i)
  
  def make (self):

    self.counts.combined = [ self.counts.computed [level] + self.counts.additional [level] for level in self.levels ]
    self.indices.make (self.counts)
  
  def append (self):
    
    self.counts.computed   = [ self.counts.computed [level] + self.counts.additional [level] for level in self.levels ]
    self.counts.additional = [ 0 for level in self.levels ]

  def strip (self):

    self.counts.additional = [ 0 for level in self.levels ]

  def manual (self):

    if helpers.query ('Do you want to manually adjust samples?', exit=0) != 'y':
      modified = False
      return modified

    else:

      message = 'specify the required additional number of samples (separated by spaces)'
      hint    = 'press ENTER to make no changes'
      default = str (self.counts.additional)
      parsed = 0

      while not parsed:
        samples = helpers.query (message, hint=hint, type=str, default=default, exit=0)
        modified = samples != default
        if modified:
          samples = samples.split (' ')
          if len (samples) != len (self.levels):
            helpers.warning ('Input not recognized, please try again:')
            continue
          else:
            parsed = 1
          for level in self.levels:
            self.counts.additional [level] = int (samples [level])
          self.available = 1
        else:
          parsed = 1

      return modified

  def load (self, config):
    
    self.history = {}
    execfile ( os.path.join (config.root, self.samples_file), globals(), self.history )

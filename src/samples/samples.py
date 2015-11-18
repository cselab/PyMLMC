
# # # # # # # # # # # # # # # # # # # # # # # # # #
# General samples classes
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers

import numpy

class Counts (object):
  
  computed   = []
  additional = []
  combined   = []
  loaded     = []
  failed     = []

class Indices (object):
  
  computed   = []
  additional = []
  combined   = []
  loaded     = []
  
  def make (self, counts):
    
    self.computed   = [ range ( 0,                       counts.computed [level] ) for level in range(len(counts.computed)) ]
    self.additional = [ range ( counts.computed [level], counts.computed [level] + counts.additional [level] ) for level in range(len(counts.additional)) ]
    self.combined   = [ range ( 0,                       counts.combined [level] ) for level in range(len(counts.combined)) ]

class Samples (object):
  
  samples_file = 'samples.dat'
  available    = 0
  
  def setup (self, levels, works):
    
    # store configuration
    vars (self) .update ( locals() )
    
    # 'sample' is treated as a _pair_ of fine and coarse samples
    self.works [1:] = [ works [level] + works [level-1] for level in self.levels [1:] ]

    self.counts  = Counts ()
    self.indices = Indices ()
    
    self.L       = len(levels) - 1

    self.counts.computed = numpy.zeros ( len(self.levels), dtype=int )

    self.counts.loaded  = [ None for level in self.levels ]
    self.counts.failed  = [ None for level in self.levels ]

    self.indices.loaded = [ None for level in self.levels ]
  
  def validate (self):
    
    for level in self.levels:
      if self.counts.additional [level] == 0:
        Exception (" :: ERROR: Encountered a level with no samples: counts.updated [%d] = 0" % level )

  def save (self, iteration):
    
    from helpers import dump
    dump (self.counts.computed,   '%d', 'computed',   self.samples_file, iteration)
    dump (self.counts.additional, '%d', 'additional', self.samples_file, iteration)
    dump (self.counts.combined,   '%d', 'combined',   self.samples_file, iteration)
  
  def make (self):

    self.counts.combined = self.counts.computed + self.counts.additional
    self.indices.make (self.counts)
  
  def append (self):
    
    self.counts.computed = [ self.counts.computed [level] + self.counts.additional [level] for level in self.levels ]
  
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
        else:
          parsed = 1

      return modified

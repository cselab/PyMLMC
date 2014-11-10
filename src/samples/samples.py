
# # # # # # # # # # # # # # # # # # # # # # # # # #
# General samples classes
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Counts (object):
  
  computed   = []
  additional = []

class Indices (object):
  
  computed   = []
  additional = []
  
  def make (self, counts):
    
    self.computed   = [ range ( 0,                       counts.computed [level] ) for level in range(len(counts.computed)) ]
    self.additional = [ range ( counts.computed [level], counts.computed [level] + counts.additional [level] ) for level in range(len(counts.additional)) ]

class Samples (object):
  
  tol          = None
  samples_file = 'samples.dat'
  
  def setup (self, levels, works):
    
    # store configuration
    vars (self) .update ( locals() )
    
    self.counts  = Counts ()
    self.indices = Indices ()
    
    self.L       = len(levels) - 1
  
  def validate (self):
    
    for level in self.levels:
      if self.counts.additional [level] == 0:
        Exception (" :: ERROR: Encountered a level with no samples: counts.updated [%d] = 0" % level )
  
  def save (self):
    
    from helpers import dump
    dump (self.counts.computed,   '%d', 'computed',   self.samples_file)
    dump (self.counts.additional, '%d', 'additional', self.samples_file)
  
  def make (self):
    
    self.indices.make (self.counts)
  
  def append (self):
    
    self.counts.computed += self.counts.additional

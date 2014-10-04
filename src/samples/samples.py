
# # # # # # # # # # # # # # # # # # # # # # # # # #
# General samples classes                        #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Counts (object):
  
  def __init__ (self):
    
    self.computed   = []
    self.additional = []

class Indices (object):
  
  def __init__ (self):
    
    self.computed   = []
    self.additional = []

class Samples (object):
  
  def __init__ (self):
    
    self.counts  = Counts  ()
    self.indices = Indices ()
  
  def validate (self):
    
    for level in self.levels:
      if self.counts.additional [level] == 0:
        Exception (" :: ERROR: Encountered a level with no samples: counts.updated [%d] = 0" % level )
    
    self.indices ()
  
  def indices (self):
    
    self.indices.computed   = [ range ( 0,                            self.counts.computed [level] ) for level in self.levels ]
    self.indices.additional = [ range ( self.counts.computed [level], self.counts.computed [level] + self.counts.additional [level] ) for level in self.levels ]

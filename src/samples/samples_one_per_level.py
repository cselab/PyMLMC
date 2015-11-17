
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (one sample per each level)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from samples import *

class One_Per_Level (Samples):
  
  def init (self):

    self.counts.additional = [ 1 for level in self.levels ]
  
  def finished (self, errors):
    return 1

  def report (self):

    print
    print ' :: SAMPLES: (one sample per each level)'

    print '    -> Number of samples for each level:'
    print '      ',
    for level in self.levels:
      print '%d' % self.counts.additional [level],
    print
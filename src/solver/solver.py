
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base Solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from os impport getcwd

class Solver (object):
  
  # return the name of a particular run
  def name (self, level, type, sample, id):
    return 'level=%d_type=%d_sample=%d_id=%d' % ( level, type, sample, id )
  
  # return the directory for a particular run
  def directory (self, level, type, sample, id):
    return getcwd () + '/' + self.name ( level, type, sample, id )
  
  # return the label (i.e. short name) of a particular run
  def label (self, prefix, level, type, sample):
    return '%s_%d_%d_%d' % (prefix, level, type, sample)

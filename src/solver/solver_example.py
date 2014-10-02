
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Solver class (example)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import subprocess, numpy, os

class Example_Solver (Solver):
  
  def __init__ (self):
    self.cmd  = '$RANDOM'
    self.filename = 'output_$(name)s'
    self.args = '> output_$(name)s'
    self.indicator = lambda x : x
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    return 1
  
  def run (self, level, type, sample, discretization, params, run_id):
    cmd_config = {}
    cmd_config ['name'] = self.name (level, type, sample, run_id)
    subprocess.call ( [self.cmd, self.args % cmd_config] )
  
  def load (self, leve, type, sample, run_id):
    filename = self.filename % self.name (level, type, sample, run_id)
    if os.path.exists ( filename ):
      f = open ( filename, 'r' )
      #return numpy.read_from_file(f)
      return 1 
    else:
      Exception ( ' :: ERROR: sample %d form level %d of type %d could not be loaded (run_id is %d) !' % (level, type, sample, run_id) )


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Solver class (example)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import subprocess, numpy

class Example_Solver (Solver):
  
  def __init__ (self):
    self.cmd  = '$RANDOM'
    self.filename = 'output_$(name)s'
    self.args = '> output_$(name)s'
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    return 1
  
  def run (self, level, type, sample, discretization, params, run_id):
    cmd_config = {}
    cmd_config ['name'] = self.name (level, type, sample, run_id)
    subprocess.call ( [self.cmd, self.args % cmd_config] )
  
  def load (self, leve, type, sample, run_id):
    f = open ( self.filename % self.name (level, type, sample, run_id), 'r' )
    return numpy.read_from_file(f) 

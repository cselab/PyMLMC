
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Solver class (example)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === Discretization format:
# {'NX' : ?, 'NY' : ?, 'NZ' : ?, 'T' : ?}

import subprocess

class Example_Solver (Solver):
  
  def __init__ (self):
    self.cmd = '$RANDOM > output_%(name)s'
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    return d ['NX'] * d ['NY'] * d ['NZ'] * d['NX'] * T
  
  def run (self, level, type, sample, discretization, params, run_id):
    
    call = self.cmd
    
    subprocess.
    counts  [level] = 1
    indices [level] = [1]

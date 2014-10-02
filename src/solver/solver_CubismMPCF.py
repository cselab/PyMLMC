
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Solver class (CubismMPCF)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === Discretization format:
# discretization = {'NX' : ?, 'NY' : ?, 'NZ' : ?, 'NS' : ?}

import subprocess

class Example_Solver (Solver):
  
  def __init__ (self):
    self.cmd = 'mpcf-cluster -name %(name)s'
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    return d ['NX'] * d ['NY'] * d ['NZ'] * d['NS']
  
  def run (self, level, type, sample, id, discretization, params):
    
    call = self.cmd

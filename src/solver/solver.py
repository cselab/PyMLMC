
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base Solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import subprocess
import shutil

class Data (object):
  
  def __init__ (self):
    self.meta = {}
    self.data = {}
  
  def __iadd__ (self, a):
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] += a.data [key] [step]
  
  def __isub__ (self):
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] -= a.data [key] [step]

class Solver (object):
  
  # return the name of a particular run
  def name (self, level, type, sample, id):
    return 'level=%d_type=%d_sample=%d_id=%d' % ( level, type, sample, id )
  
  # return the directory for a particular run
  def directory (self, level, type, sample, id):
    return os.getcwd () + '/' + self.name ( level, type, sample, id )
  
  # return the label (i.e. short name) of a particular run
  def label (self, prefix, level, type, sample):
    return '%s_%d_%d_%d' % (prefix, level, type, sample)
  
  # execute the command
  def execute (self, cmd, directory):
    
    # create directory
    os.mkdir ( directory )
    
    # copy needed input files
    for inputfile in self.inputfiles:
      shutil.copy ( inputfile, directory + '/' )
    
    # execute command
    with open ( os.devnull, 'w' ) as devnull:
      subprocess.check_call ( cmd, cwd=directory, stdout=devnull, stderr=subprocess.STDOUT, shell=True, env=os.environ.copy() )


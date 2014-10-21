
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base Solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import sys
import subprocess
import shutil
import pprint

class Results (object):
  
  def __init__ (self):
    self.meta = {}
    self.data = {}
  
  def __iadd__ (self, a):
    if self.data == {}:
      self.zeros (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] += a.data [key] [step]
    return self
  
  def __isub__ (self, a):
    if self.data == {}:
      self.zeros (a)
    for key in self.data.keys():
      for step in xrange ( len ( self.data [key] ) ):
        self.data [key] [step] -= a.data [key] [step]
    return self
  
  def zeros (self, a):
    self.meta = a.meta
    for key in a.data.keys():
      self.data [key] = []
      for step in xrange ( len ( a.data [key] ) ):
        self.data [key] .append ( 0 )
  
  def __str__ (self):
    output = '\n' + 'meta:'
    for key in self.meta.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.meta [key]) ) % tuple ( [ '%1.1e' % value for value in self.meta [key] ] ) )
    output += '\n' + 'data:'
    for key in self.data.keys():
      output += '\n %10s :%s' % ( str (key), ( '%8s' * len (self.data [key]) ) % tuple ( [ '%1.1e' % value for value in self.data [key] ] ) )
    return output

class Solver (object):
  
  # set default path
  def setpath (self):
    if not self.path:
      try:
        self.path = os.environ [self.pathvar] + '/'
      except:
        print ' :: ERROR: executable path not set in %s.' % self.pathvar
        sys.exit()
  
  # return the name of a particular run
  def name (self, level, type, sample, id):
    return 'level=%d_type=%d_sample=%d_id=%d' % ( level, type, sample, id )
  
  # return the directory for a particular run
  def directory (self, level, type, sample, id, deterministic=0):
    if deterministic:
      return '.'
    else:
      return self.name ( level, type, sample, id )
  
  # return the label (i.e. short name) of a particular run
  def label (self, prefix, level, type, sample):
    return '%s_%d_%d_%d' % (prefix, level, type, sample)
  
  # execute the command
  def execute (self, cmd, directory, params):
    
    # create directory
    if directory != '.':
      try:
        os.mkdir ( directory )
      except:
        print
        print ' :: ERROR: working directory is NOT clean!'
        print '  : -> Remove all directories like "%s".' % directory
        print
        sys.exit()
    
    # copy needed input files
    for inputfile in self.inputfiles:
      shutil.copy ( inputfile, directory + '/' )
    
    # report full submission command
    if params.verbose >= 1:
      print
      print cmd
      print
    
    # set stdout based on verbosity level
    if params.verbose >= 2:
      stdout = None
    else:
      stdout = open ( os.devnull, 'w' )
    
    # execute command
    subprocess.check_call ( cmd, cwd=directory, stdout=stdout, stderr=subprocess.STDOUT, shell=True, env=os.environ.copy() )

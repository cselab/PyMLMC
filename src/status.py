
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Status class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import os
import sys

# === local imports

import local
import helpers

# === Status class

class Status (object):
  
  def __init__ (self):
    
    self.status_file = 'status.dat'
  
  # save status
  def save (self, config):
  
    with open ( os.path.join (config.root, self.status_file), 'w' ) as f:
      
      f.write ( 'samples  = [ ' + ''.join ( [ str (config.samples.counts.computed [level]) + ', ' for level in config.levels ] ) + ']\n' )
      if not config.deterministic:
        f.write ( 'tol      = ' + str (config.samples.tol) + '\n' )
      f.write ( 'batch = %s' % str (config.scheduler.batch)  + '\n' )
      if 'cluster' in self.list:
        f.write ( 'cluster = \'%s\'' % self.status ['cluster']  + '\n' )
      else:
        f.write ( 'cluster = \'%s\'' % local.name  + '\n' )
      try:
        f.write ( 'parallelization = \'%s\'' % config.scheduler.parallelizations [config.L] [config.FINE] .cores + '\n' )
      except:
        f.write ( 'parallelization = \'%s\'' % self.list ['parallelization'] + '\n' )
      try:
        walltimes = helpers.level_type_list (config.levels)
        for level, type in config.levels_types:
          walltimes [level] [type] = config.scheduler.parallelizations [config.L] [config.FINE] .walltime
        f.write ( 'walltimes = %s' % walltimes + '\n' )
      except:
        f.write ( 'walltimes = %s' % self.list ['walltimes'] + '\n' )
    
    print
    print (' :: INFO: MLMC status saved to %s' % os.path.join (config.root, self.status_file))
  
  # load status
  def load (self, config):
    
    try:
    
      self.list = {}
      execfile ( os.path.join (config.root, self.status_file), globals(), self.list )
      
      config.samples.counts.computed = self.list ['samples']
      config.samples.make ()
      
      if not config.deterministic:
        if config.samples.tol != self.list ['tol']:
          print
          print (' :: WARNING: The requested tolerance is different from the tolerance in the in status file.')
          print ('  : -> Tolerance from the status file will be used.')
        config.samples.tol = self.list ['tol']
      
      config.scheduler.batch = self.list ['batch']
      
      if 'cluster' not in self.list:
        self.list ['cluster'] = 'unknown'
      
      if 'parallelization' not in self.list:
        self.list ['parallelization'] = 'unknown'
      
      if 'walltimes' not in self.list:
        walltimes = helpers.level_type_list (config.levels)
        for level, type in config.levels_types:
          walltimes [level] [type] = 'unknown'
        self.list ['walltimes'] = walltimes
      
      print
      print (' :: INFO: MLMC status loaded from')
      print ('  : %s' % os.path.join (config.root, self.status_file))
    
    except:
      
      print
      print (' :: ERROR: MLMC status could not be loaded from')
      print ('  : %s' % os.path.join (config.root, self.status_file))
      print ('  : -> Run PyMLMC with \'-r\' option to restart the simulation')
      print
      
      sys.exit()

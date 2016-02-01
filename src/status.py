
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
    self.list        = {}
  
  # save status
  def save (self, config):
  
    with open ( os.path.join (config.root, self.status_file + ('' if config.deterministic else '.%d' % config.iteration)), 'w' ) as f:

      f.write ( 'iteration = %d\n' % config.iteration )

      f.write ( 'samples  = [ ' + ''.join ( [ str (config.samples.counts.computed   [level]) + ', ' for level in config.levels ] ) + ']\n' )
      f.write ( 'pending  = [ ' + ''.join ( [ str (config.samples.counts.additional [level]) + ', ' for level in config.levels ] ) + ']\n' )
      f.write ( 'combined = [ ' + ''.join ( [ str (config.samples.counts.combined   [level]) + ', ' for level in config.levels ] ) + ']\n' )

      #if not config.deterministic:
      #  f.write ( 'tol      = ' + str (config.samples.tol) + '\n' )

      batch = helpers.level_type_list (config.levels)
      for level, type in config.levels_types:
        if config.scheduler.parallelizations [level] [type] .batch:
          batch [level] [type] = config.scheduler.parallelizations [level] [type] .batchmax
        else:
          batch [level] [type] = None
      f.write ( 'batch = %s' % batch + '\n' )

      f.write ( 'merge = %s' % str (config.scheduler.merge)  + '\n' )

      if 'cluster' in self.list:
        f.write ( 'cluster = \'%s\'' % self.list ['cluster']  + '\n' )
      else:
        f.write ( 'cluster = \'%s\'' % local.name  + '\n' )

      cores = helpers.level_type_list (config.levels)
      for level, type in config.levels_types:
        cores [level] [type] = config.scheduler.parallelizations [level] [type] .cores
      f.write ( 'parallelization = %s' % cores + '\n' )

      f.write ( 'works = %s' % str(config.works) + '\n' )

      walltimes = helpers.level_type_list (config.levels)
      for level, type in config.levels_types:
        walltimes [level] [type] = config.scheduler.parallelizations [level] [type] .walltime
      f.write ( 'walltimes = %s' % walltimes + '\n' )

    print
    print (' :: INFO: MLMC status saved to %s' % os.path.join (config.root, self.status_file))
  
  # load status
  def load (self, config):

    # look for status files
    from glob import glob
    statusfiles = glob ( os.path.join (config.root, self.status_file + '*') )
    if len (statusfiles) == 0:
      raise

    # use the most recent status file
    self.list = {}
    execfile ( statusfiles [-1], globals(), self.list )

    # check if the number of levels is the same
    if len (self.list ['samples']) != len (config.levels):
      helpers.error ('Number of levels does not match: %d (status file) and %d (specified)' % (len (self.list ['samples']), len (config.levels)) )

    config.iteration = self.list ['iteration']
    config.solver.iteration = self.list ['iteration']
    
    config.samples.counts.computed   = self.list ['samples']
    config.samples.counts.additional = self.list ['pending']
    config.samples.make ()
    '''
    if not config.deterministic:
      if config.samples.tol != self.list ['tol']:
        print
        print (' :: WARNING: The requested tolerance is different from the tolerance in the in status file.')
        print ('  : -> Tolerance from the status file will be used.')
      config.samples.tol = self.list ['tol']
    '''

    config.scheduler.batch = self.list ['batch']
    config.scheduler.merge = self.list ['merge']
      
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
    if not config.deterministic:
      print ('  : Simulation iteration: %d' % config.iteration )
    print ('  : Simulation was executed on \'%s\'' % self.list ['cluster'] )
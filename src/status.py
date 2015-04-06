
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

# === local imports

import local

# === Status class

class Status (object):
  
  def __init__ (self, levels):
    
    self.levels      = levels
    self.L           = len(levels) - 1
    self.status_file = 'status.dat'
  
  # save status
  def save (self, config):
  
    with open ( os.path.join (config.root, self.status_file), 'w' ) as f:
      
      f.write ( 'samples  = [ ' + ''.join ( [ str (config.samples.counts.computed [level]) + ', ' for level in self.levels ] ) + ']\n' )
      if not config.deterministic:
        f.write ( 'tol      = ' + str (config.samples.tol) + '\n' )
      f.write ( 'batch = %s' % str ( config.scheduler.batch )  + '\n' )
      f.write ( 'cluster = \'%s\'' % local.name  + '\n' )
      try:
        f.write ( 'parallelization = %s' % config.scheduler.parallelizations [self.L] [0] .cores + '\n' )
      except:
        f.write ( 'parallelization = %s' % status ['parallelization'] + '\n' )
      try:
        f.write ( 'walltime = %s' % config.scheduler.parallelizations [self.L] [0] .walltime + '\n' )
      except:
        f.write ( 'walltime = %s' % self.status ['walltime'] + '\n' )
    
    print
    print (' :: INFO: MLMC status saved to %s' % os.path.join (config.root, self.status_file))
  
  # load status
  def load (self, config):
    
    try:
      
      self.status = {}
      execfile ( os.path.join (self.config.root, self.status_file), globals(), self.status )
      
      config.samples.counts.computed = self.status ['samples']
      config.samples.make ()
      
      if not config.deterministic:
        if config.samples.tol != self.status ['tol']:
          print
          print (' :: WARNING: The requested tolerance is different from the tolerance in the in status file.')
        config.samples.tol = self.status ['tol']
      
      config.scheduler.batch = self.status ['batch']
      
      if not 'cluster' in self.status:
        self.status ['cluster'] = 'unknown'

      if not 'parallelization' in status:
        self.status ['parallelization'] = 'unknown'

      if not 'walltime' in status:
        self.status ['walltime'] = 'unknown'
      
      self.create_MCs (config.samples.indices.computed)

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

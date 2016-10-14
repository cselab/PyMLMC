
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Scheduling using TORC tasking library
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from scheduler import *
import local
from numpy import round, floor, ceil
import os

class TORC (Scheduler):

  def __init__ ( self, nodes=None, walltime=None, cores=None, email='', ratios=None ):

    self.name      = 'TORC'
    self.walltime  = walltime
    self.nodes     = nodes
    self.cores     = cores
    self.email     = email
    self.ratios    = ratios

    self.queuefile = 'queue.dat'

  def distribute (self):

    for level, type in self.levels_types:

      # all levels are processed in batch
      self.batch [level] [type] = 1

      # no level merging to ensembles, TORC should handle this itself
      self.merge [level] [type] = 0

      # compute the required number of cores based on pre-computed ratios between resolution levels
      required = self.cores * float (self.ratios [level - type]) / float (self.ratios [self.L])

      # round the result
      cores = int ( ceil ( required ) )

      # walltime is decreased due to level (w.r.t to L) and increased due to fewer cores
      walltime = self.walltime * (float (self.works [level - type]) / self.works [self.L]) * (float (self.cores) / cores)

      # construct parallelization according to all computed parameters
      self.parallelizations [level] [type] = Parallelization ( cores, walltime, self.sharedmem, self.batch [level] [type], self.merge [level] [type], self.email )

  # dispatch all jobs
  def dispatch (self, batch, jobs, directory, label, parallelization):

    # generate file with configuration for all jobs
    queuefile = os.path.join (directory, self.queuefile)
    with open ( queuefile, 'w' ) as f:
      format = '%(directory)s %(nodes)s %(cores)s %(ranks)d %(tasks)d %(threads)d %(cmd)s\n'
      all_args = parallelization.args ()
      for args, job in zip (batch, jobs):
        all_args ['directory'] = args ['sample']
        all_args ['cmd']       = job
        f.write ( format % all_args )

    # rely on TORC to dispatch all jobs
    cmd = './torc %s' % self.queuefile

    # configure submission
    #parallelization.batch = ?
    #parallelization.merge = ?

    # submit
    #self.execute ( self.submit (batch, parallelization, label, directory, suffix=suffix, timer=1), directory )

    return 'dispatched to TORC'


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Example script for using PyMLMC with CubismMPCF solver
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === import PyMLMC

from pymlmc import *

# === configuration

# minimum values for the resolution of the coarsest level (N0)
# Brutus              32
# Cray XK6            64
# BG/Q node          128
# FERMI 64 nodes     512
# JUQ 512 nodes     1024
# MIRA 512 nodes    1024
# CETUS 128 nodes    512 (only 1 block per 2 threads)

name = 'uq100uEh'

N0 = 1024
L  = 2

tend = 1.0 # 3 us

nodes    = 8192
cores    = 16
walltime = 24

ratios   = [16, 4, 1]

email    = 'sukys.jonas@gmail.com'
separate = 0

warmup   = 1

runtime  = 24
workunit = 8192 * cores * float (runtime) / (4096 ** 4)
budget   = 8 * 8192 * cores * runtime # 24 million CPU hours

# solver
from solver_CubismMPCF import CubismMPCF
options = '-sim cloud -cfl 0.3 -verbosity 0 -gsync 128'

options += ' -kernels qpx'

options += ' -pp 12.8'
options += ' -pb 28.0'

options += ' -nsteps 0'

options += ' -analysisperiod 10'
options += ' -dumpdt 0.2'
#options += ' -saveperiod 5000'
options += ' -saveperiod 0'

options += ' -io 1'
options += ' -vp 1'
options += ' -vpeps 1e-3'
options += ' -vpchannels 45m'
options += ' -wtype 3'

#options += ' -hdf 1'
#options += ' -hdfchannels 45'

options += ' -hllc 1'
options += ' -mollfactor 1'

options += ' -g1 6.59'
options += ' -pc1 4.049e3'
options += ' -g2 1.4'
options += ' -pc2 1.0'

options += ' -extent 4'

options += ' -sensors 4'

options += ' -sensor1_rad 0.05'
options += ' -sensor1_pos_x 2.0'
options += ' -sensor1_pos_y 2.0'
options += ' -sensor1_pos_z 2.0'

options += ' -sensor2_rad 0.05'
options += ' -sensor2_pos_x 2.3'
options += ' -sensor2_pos_y 2.0'
options += ' -sensor2_pos_z 2.0'

options += ' -sensor3_rad 0.05'
options += ' -sensor3_pos_x 2.7'
options += ' -sensor3_pos_y 2.0'
options += ' -sensor3_pos_z 2.0'

options += ' -sensor4_rad 0.05'
options += ' -sensor4_pos_x 2.9'
options += ' -sensor4_pos_y 2.0'
options += ' -sensor4_pos_z 2.0'

import os, subprocess

def cloud (directory, seed):
  
  # cloud setup
  extent = 4
  rmin   = 0.075
  rmax   = 0.075
  count  = 100
  beta   = 1000
  alpha  = 0.01
  target = 'beta'

  envelope  = 'sphere'
  exclusion = 'none'
  zoom      = 1.0
  NX        = 0
  proximity = rmin
  
  cloud_pos_x = 2.0
  cloud_pos_y = 2.0
  cloud_pos_z = 2.0
  cloud_rad   = 1.0

  # create cloud configuration file
  with open ( directory + '/cloud.cfg', 'w' ) as f:

    f.write ( 'size %d\n' % count )
    f.write ( 'target %s\n' % target )
    f.write ( 'beta %f\n' % beta )
    f.write ( 'alpha %f\n' % alpha )

    f.write ( 'extent_x %f\n' % extent )
    f.write ( 'extent_y %f\n' % extent )
    f.write ( 'extent_z %f\n' % extent )

    f.write ( 'periodic_x 0\n' )
    f.write ( 'periodic_y 0\n' )
    f.write ( 'periodic_z 0\n' )
  
    f.write ( 'structured no\n' )

    f.write ( 'r_min %f\n' % rmin )
    f.write ( 'r_max %f\n' % rmax )

    f.write ( 'envelope %s\n' % envelope )
    f.write ( 'exclusion %s\n' % exclusion )

    f.write ( 'zoom %f\n' % zoom )
    f.write ( 'seed %d\n' % seed )
    f.write ( 'NX %d\n' % NX )
    f.write ( 'proximity %f\n' % proximity )

    f.write ( 'cloud_pos_x %f\n' % cloud_pos_x )
    f.write ( 'cloud_pos_y %f\n' % cloud_pos_y )
    f.write ( 'cloud_pos_z %f\n' % cloud_pos_z )
    f.write ( 'cloud_rad   %f\n' % cloud_rad   )

  # run cloud generation
  cmd       = 'cloud-cell-list cloud.cfg'
  verbose   = 0
  if verbose:
    stdout = None
    stderr = None
  else:
    stdout = open ( os.devnull, 'w' )
    stderr = subprocess.STDOUT 
  subprocess.check_call ( cmd, cwd=directory, stdout=stdout, stderr=stderr, shell=True, env=os.environ.copy() )

# discretizations
grids = helpers.grids_3d ( helpers.grids (N0, L) )

# samples
from samples_estimated_budget import Estimated_Budget

# scheduler
from scheduler_static import Static

# assemble MLMC configuration
config = Config ()
config.solver          = CubismMPCF (tend, options, name=name, workunit=workunit, init=cloud)
config.discretizations = grids
config.samples         = Estimated_Budget (budget, warmup)
config.scheduler       = Static (nodes, walltime, email=email, separate=separate)
config.ratios          = ratios

# === simulation

# create MLMC simulation
mlmc = MLMC (config)

# check if interactive
if __name__ == '__main__':

  # run MLMC simulation
  mlmc.simulation()

# === results and analysis

# check if interactive
if __name__ == '__main__':

  from plot import *

  # setup
  set_extent  (2.0)
  set_surface (1.0)
  
  qois = {}
  qois ['p_max'] = [-1500, 4000]
  qois ['p_max_pos_d'] = None
  qois ['p_sen1'] = qois ['p_max']
  qois ['p_sen2'] = qois ['p_max']
  qois ['p_sen3'] = qois ['p_max']
  qois ['p_sen4'] = qois ['p_max']
  qois ['V2'   ] = [0, 0.2]
  qois ['V2_50'] = [0, 0.2]
  qois ['V2_vf'] = [0, 0.2]
  qois ['c_max'] = [0, 15.0]
  qois ['c_sen1'] = qois ['c_max']
  qois ['c_max_pos_d'] = None
  qois ['m_max'] = [0, 3]
  qois ['M_max'] = [0, 3]
  qois ['M_sen1'] = qois ['M_max']
  qois ['ke_avg'] = [0, 0.5]

  # plotting emnsembles
  for qoi, extent in qois.iteritems():
    plot_ensembles ( mlmc, qoi=qoi, extent=extent, save=figname('ensembles') )

  # show ensembles
  if not local.cluster:
    show()
   
  # statistics
  from stats_numpy import *
  stats = []
  stats.append ( NumPy_Stat ('mean') )
  stats.append ( NumPy_Stat ('percentile', '0.05 percentile',  5) )
  stats.append ( NumPy_Stat ('percentile', '0.95 percentile', 95) )
  
  # assemble MLMC estimates
  mlmc.assemble (stats, qois.keys())
  
  for qoi, extent in qois.iteritems():

    # plot MC results
    plot_mcs ( mlmc, qoi=qoi, extent=extent, save=figname('stats_mcs') )

    # plot diffs of MC results
    plot_diffs ( mlmc, qoi=qoi, extent=extent, save=figname('stats_diffs') )

    # plot MLMC results
    plot_mlmc ( mlmc, qoi=qoi, extent=extent, save=figname('stats_mlmc') )
  
  if not local.cluster:
    show()

  # plot samples
  plot_samples ( mlmc, infolines=False, save=figname('samples') )
  
  # plot budget
  plot_budget ( mlmc, infolines=False, save=figname('budget') )

  # plot indicators
  plot_indicators ( mlmc, infolines=False, save=figname('indicators') )

  # plot correlations
  plot_correlations ( mlmc, infolines=False, save=figname('correlations') )

  # plot errors
  plot_errors ( mlmc, infolines=False, save=figname('errors') )
 
  if not local.cluster:
    show()

  query()

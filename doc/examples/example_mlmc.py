
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Example script for using PyMLMC with simple 2D stochastic integral
#
# For each sample, specified by parameters (level, type, sample, id),
# a directory is created and the run (together with input and output)
# is sandboxed (restricted) to that directory.
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === import PyMLMC

from pymlmc import *

# === global configuration

name  = 'int2d'

N0 = 8          # resolution on the coarsest discretization level 0
L  = 4          # finest level (levels = 0, ..., L)

cores    = 1    # requested number of cores (for a single sample on the finest level L)
walltime = 1    # requested walltime in hours (for a single sample on the finest level L)

warmup   = 4    # number of warmup samples on the finest level L
budget   = 0.1  # prescribed total (warmup AND update stages) computational budget (in core hours) for all samples on all levels

# === modules configuration

# general
config = MLMC_Config ()
config.deterministic = 0    # simulation runs directly in 'output' directory and the update phases are skipped

# solver
from solver_Integral2D import Integral2D
config.solver = Integral2D (name=name, workunit=workunit)

# discretizations
config.discretizations = helpers.grids (N0, L)

# samples
from samples_estimated_budget import Estimated_Budget
config.samples = Estimated_Budget (budget, warmup)

# scheduler
from scheduler_static import Static
config.scheduler = Static (cores=cores, walltime=walltime)

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

  from plot_matplotlib import MatPlotLib

  # initialize plotting backend
  plot = MatPlotLib ( mlmc, autosave=1 )

  # quantities of interest to be plotted and (optionally) their extents (can be set to 'None')
  qois = { 'I' : [0, 1] }

  # plotting emnsembles
  for qoi, extent in qois.iteritems():
    plot.ensembles ( qoi=qoi, extent=extent, both=0 )
    plot.ensembles ( qoi=qoi, extent=extent, both=1 )

  # show ensembles
  if not local.cluster:
    plot.show()
  
  # required qoi ranges for MLMC estimates
  ranges = []
  ranges.append ( ['I', 0, None] )

  # statistics
  from stats_numpy import NumPy_Stat
  from stats_confidence import Confidence
  from stats_deviations import Deviations
  from stats_histogram import Histogram
  figures = {}
  figures ['median-confidence'] = [ NumPy_Stat ('median'), Confidence (level=0.25), Confidence (level=0.05) ]
  figures ['mean-deviations']   = [ NumPy_Stat ('mean'), Deviations (factor=1), Deviations (factor=2) ]
  figures ['histogram']         = [ Histogram () ]

  # assemble and plot all statistics
  for suffix, stats in figures.iteritems():

    # indicate current figure
    print
    print ' :: Figure: %s' % suffix

    # assemble MLMC estimates
    mlmc.assemble ( stats, qois )
    
    # clip MLMC estimates
    mlmc.clip (ranges)
    
    # plot all qois
    for qoi, extent in qois.iteritems():

      # plot MC results
      plot.stats_mcs ( qoi=qoi, extent=extent, suffix=suffix )

      # plot diffs of MC results
      plot.stats_diffs ( qoi=qoi, extent=extent, suffix=suffix )

      # plot MLMC results
      plot.stats_mlmc ( qoi=qoi, extent=extent, suffix=suffix )
    
    # show statistics
    if not local.cluster:
      plot.show()

  # plot samples
  plot.samples ()

  # plot budget
  plot.budget ()

  # plot indicators
  plot.indicators ()

  # plot correlations
  plot.correlations ()

  # plot coefficients
  plot.coefficients ()

  # plot errors
  plot.errors ()

  # show indicators
  if not local.cluster:
    plot.show()

  # query for further action
  plot.query()

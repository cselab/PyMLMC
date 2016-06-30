
# === import PyMLMC

from pymlmc import *

# === global configuration

name  = 'int2d'
email = 'sukys.jonas@gmail.com'

N0 = 8          # coarsest resolution
L  = 4          # finest level (levels = 0, ..., L)

cores    = 4    # requested number of cores
walltime = 1    # requested walltime (in hours)

warmup   = 4    # number of warmup samples on the finest level L

workunit = 0.1  # estimated workunit (in core hours), such that runtime = workunit * solver.work (resolution)
budget   = 10   # prescribed total budget (in core hours) for all samples on all levels

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
config.scheduler = Static (cores=cores, walltime=walltime, email=email)

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
  plot = MatPlotLib (mlmc)

  # setup plotting
  plot.autosave = 1
  plot.set_extent  (10.0)
  plot.set_surface (2.5)

  qois = { 'I' : [0, 1], ??? }

  # plotting emnsembles
  for qoi, extent in qois.iteritems():
    plot.ensembles ( qoi=qoi, extent=extent )

  # show ensembles
  if not local.cluster:
    plot.show()

  # statistics
  from stats_numpy import *
  stats = []
  stats.append ( NumPy_Stat ('mean') )
  stats.append ( NumPy_Stat ('percentile', '0.05 percentile',  5) )
  stats.append ( NumPy_Stat ('percentile', '0.95 percentile', 95) )

  # TOOD: add histograms as image plots?
  #stats.append ( NumPy_Stat ('histogram') )

  # assemble MLMC estimates
  mlmc.assemble (stats, qois.keys())

  # required qoi ranges for MLMC estimates
  ranges = []
  ranges.append ( ['I', 0, None] )

  # clip MLMC estimates
  mlmc.clip (ranges)

  for qoi, extent in qois.iteritems():

    # plot MC results
    plot.mcs ( qoi=qoi, extent=extent )

    # plot diffs of MC results
    plot.diffs ( qoi=qoi, extent=extent )

    # plot MLMC results
    plot.mlmc ( qoi=qoi, extent=extent )

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

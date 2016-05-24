
# === import PyMLMC

from pymlmc import *

# === global configuration

name  = 'Integral2D'
email = 'sukys.jonas@gmail.com'

N0 = 8          # coarsest resolution
L  = 4          # finest level (levels = 0, ..., L)

cores    = 4    # requested number of cores
walltime = 1    # requested walltime (in hours)

warmup   = 4    # number of warmup samples on the finest level L

workunit = 0.1  # estimated workunit (in core hours), such that runtime = workunit * solver.work (resolution)
budget   = 10   # prescribed total budget (in core hours) for all samples on all levels

# === MLMC configuration

config = MLMC_Config ()

# solver
from solver_example import Integral2D
config.solver = CubismMPCF (name=name, workunit=workunit)

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

  from plot import *

  qois = { 'I' : [0, 1], ??? }

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

  # TOOD: add histograms?
  #stats.append ( NumPy_Stat ('histogram') )

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
  plot_samples ( mlmc, save=figname('samples') )

  # plot budget
  plot_budget ( mlmc, save=figname('budget') )

  # plot indicators
  plot_indicators ( mlmc, save=figname('indicators') )

  # plot correlations
  plot_correlations ( mlmc, save=figname('correlations') )

  # plot coefficients
  plot_coefficients ( mlmc, save=figname('coefficients') )

  # plot errors
  plot_errors ( mlmc, save=figname('errors') )
  
  if not local.cluster:
    show()
  
  query()

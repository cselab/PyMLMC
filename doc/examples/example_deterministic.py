
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Example script for using PyMLMC for single deterministic runs
#
# Simulation runs directly in 'output' directory and the update phases are skipped
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === import PyMLMC

from pymlmc import *

# === global configuration

name = 'int2d'

discretization = 8    # discretization
cores          = 1    # requested number of cores
walltime       = 1    # requested walltime in hours

# === modules configuration

# general
config.deterministic = 1

# solver
from solver_Integral2D import Integral2D
config.solver = Integral2D (name=name)

# discretizations
config.discretizations = [discretization, ]

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
    plot.plot ( qoi=qoi, extent=extent )

  # show ensembles
  if not local.cluster:
    plot.show()

  # query for further action
  plot.query()

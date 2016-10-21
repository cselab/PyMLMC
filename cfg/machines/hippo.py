
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Hippo (Dalco Raid 6 storage server)
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Hippo (CSE lab)'

# Hippo is not a cluster
cluster = 0

# default configuration
cores     = 4    # per node
threads   = 1    # per core
walltime  = None # hours
memory    = None # GB per core

# constraints
bootup       = None
min_cores    = 1
max_cores    = 4

def min_walltime (cores): # hours
  return None

def max_walltime (cores): # hours
  return None

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# core performance metric (normalized w.r.t. IBM BG/Q)
performance = 1

# scratch path
scratch = None

# ensemble support
ensembles = 0

# default environment variables
envs = ''

# run command
simple_job = 'ulimit -c 0; export OMP_NUM_THREADS=%(threads)d; %(envs)s %(cmd)s'

# MPI run command
mpi_job = 'ulimit -c 0; export OMP_NUM_THREADS=%(threads)d; %(envs)s mpirun -np %(ranks)d %(cmd)s'

# submission script template
script = None

# submit command
submit = '%(job)s'

# timer
timer = '(time -p (%(job)s)) 2>&1 | tee %(timerfile)s'

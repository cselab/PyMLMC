
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Mac
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Mac'

# Mac is (usually) not a cluster
#TODO: this was modified for testing purposes
cluster = 1

# default configuration
cores     = 2    # per node
threads   = 1    # per core
walltime  = None # hours
memory    = None # GB per core

# constraints
bootup       = None
min_walltime = None
max_walltime = None
min_cores    = 1

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# scratch path
scratch = None

# default environment variables
envs = ''

# run command
simple_job = 'ulimit -c 0; export OMP_NUM_THREADS=%(threads)d; %(envs)s %(cmd)s %(options)s'

# MPI run command
mpi_job = 'ulimit -c 0; export OMP_NUM_THREADS=%(threads)d; %(envs)s mpirun -np %(ranks)d %(cmd)s %(options)s'

# submission script template
script = None

# submit command
submit = '%(job)s'

# timer
timer = 'time'

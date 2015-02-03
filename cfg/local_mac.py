
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
cores    = 2
threads  = 2
walltime = None
memory   = None

# constraints
bootup = None

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

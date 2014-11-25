
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
walltime_min = None

# run command
simple_job = 'export OMP_NUM_THREADS=%(threads)d; %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; mpirun -np %(ranks)d %(cmd)s %(options)s'

# batch run command
batch_job = '%(batch)s'

# submit command
submit = '%(job)s'

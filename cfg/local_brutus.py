
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Mac
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Brutus + GCC'

# Brutus is a cluster
cluster = 1

# default configuration
cores     = 1
threads   = 12
walltime  = 1
memory    = 1024

# simple run command
job = '%(cmd)s %(options)s'

# MPI run command
mpi_job = 'mpirun -np %(ranks)d -pernode %(cmd)s %(options)s'

# submit command
submit = 'export OMP_NUM_THREADS=%(threads)d; bsub -n %(cores)d -R "span[ptile=%(threads)d]" -W %(walltime-hours)d:%(walltime-minutes)d -R "rusage[mem=%(memory)d]" %(job)s'

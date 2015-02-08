
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Brutus cluster
# More information: http://www.clusterwiki.ethz.ch/brutus/Brutus_wiki
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'ETH Brutus'

# Brutus is a cluster
cluster = 1

# default configuration
cores     = 48   # per node
threads   = 1    # per core
walltime  = 1    # hours
memory    = 1024 # GB per core
rack      = 1024 # nodes

# constraints
bootup       = 5  # minutes
min_walltime = 0  # hours
max_walltime = 36 # hours (could be more (7d), but then there is a limit on cores)
min_cores    = 1

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# scratch path
scratch = '/cluster/scratch_xp/public/sukysj/pymlmc'

# default environment variables
envs = ''

# simple run command
simple_job = 'ulimit -c 0; export OMP_NUM_THREADS=%(threads)d; %(envs)s %(cmd)s %(options)s'

# MPI run command
mpi_job = 'ulimit -c 0; %(envs)s mpirun -np %(ranks)d --npernode %(tasks)d --cpus-per-proc %(threads)d %(cmd)s %(options)s'

# submission script template
script = None

# submit command
submit = 'ulimit -c 0; export OMP_NUM_THREADS=%(threads)d; bsub -n %(cores)d -R "span[ptile=%(threads)d]" -W %(hours).2d:%(minutes).2d -R "rusage[mem=%(memory)d]" -J %(label)s -oo report.%(label)s %(xopts)s < %(jobfile)s'

# timer
timer = 'date; time'

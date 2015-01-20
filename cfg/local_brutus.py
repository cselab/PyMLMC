
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Brutus cluster
# More information: http://www.clusterwiki.ethz.ch/brutus/Brutus_wiki
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
cores     = 48
threads   = 48
walltime  = 1
memory    = 1024

# constraints
bootup = 5

# scratch path
scratch = '/cluster/scratch_xp/public/sukysj/pymlmc'

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads)d; %(cmd)s %(options)s'

# MPI run command
mpi_job = 'mpirun -np %(ranks)d --npernode %(tasks)d --cpus-per-proc %(threads)d %(cmd)s %(options)s'

# batch run command
batch_job = '< %(script)s'

# submit command
submit = 'export OMP_NUM_THREADS=%(threads)d; bsub -n %(cores)d -R "span[ptile=%(threads)d]" -W %(hours)d:%(minutes)d -R "rusage[mem=%(memory)d]" -J %(label)s -oo report.txt %(xopts)s %(job)s'

# timer is disabled (for non-batch jobs)
timer       = 0
timer_start = 'START=$(/bin/date +%s)'
timer_stop  = 'TIME=$(($(/bin/date +%s)-START)); echo Total time: $TIME seconds'
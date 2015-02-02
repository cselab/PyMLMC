
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for JUQUEEN cluster
# Jülich Supercomputing Centre (JSC)
# More information: http://www.fz-juelich.de/ias/jsc/EN/Expertise/Supercomputers/JUQUEEN
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Julich JUQUEEN (BlueGene/Q)'

# JUQUEEN is a cluster
cluster = 1

# default configuration
# todo: differentiate between cores and threads? on BG/Q that is different.. also memory should be computed per core, right?
cores     = 16
threads   = 64
walltime  = 1
memory    = 1024
rack      = 1024 # nodes

# constraints
bootup = 5

# scratch path (not required - we use $WORK)
scratch = None

# simple run command
simple_job = 'runjob --np %(ranks)d -p %(tasks)d --envs OMP_NUM_THREADS=%(threads)d --verbose=INFO: %(cmd)s %(options)s'

# MPI run command
mpi_job = 'runjob --np %(ranks)d -p %(tasks)d --envs OMP_NUM_THREADS=%(threads)d --verbose=INFO: %(cmd)s %(options)s'

# batch run command
batch_job = '%(batch)s'

# submit command
submit = 'llsubmit %(script)s'

# @ job_type = bluegene
# @ bgsize = %(nodes)s
# @ job_name = LoadL_Sample_1

# timer
timer = 'time'

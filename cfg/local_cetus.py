
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Cetus cluster
# BlueGene/Q @ Argonne National Laboratory
# More information: http://www.alcf.anl.gov/user-guides/blue-geneq-versus-blue-genep
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Argonne Cetus (BlueGene/Q)'

# Cetus is a cluster
cluster = 1

# default configuration
cores     = 16   # per node
threads   = 4    # per core
walltime  = 1    # h
memory    = 1024 # GB per core
rack      = 1024 # nodes

# constraints
bootup       = 5   # minutes
min_walltime = 0   # hours
max_walltime = 1   # hours
min_cores    = 1 * cores

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# scratch path
scratch = '/projects/CloudPredict/sukysj/pymlmc'

# default environment variables
envs = '''  --envs PAMI_DEVICE=B \
  --envs BG_MEMSIZE=16384 \
  --envs BG_THREADLAYOUT=2 \
  --envs OMP_STACKSIZE=4M \
  --envs OMP_SCHEDULE="dynamic,1" \
  --envs PAMID_COLLECTIVES=1 \
  --envs PAMI_MEMORY_OPTIMIZED=1 \
  --envs BG_SHAREDMEMSIZE=512 \
  --envs BG_MAPCOMMONHEAP=0 \
  --envs BG_SMP_FAST_WAKEUP=YES \
  --envs L1P_POLICY="dcbt" \
  --envs L1P_DEPTH=2 \
  --envs PAMID_THREAD_MULTIPLE=1 \
  --envs PAMID_VERBOSE=1 \
  --envs PAMID_MAX_COMMTHREADS=1 \
  --envs OMP_WAIT_POLICY=PASSIVE \
  --envs OMP_PROC_BIND=FALSE \
  --envs USEMAXTHREADS=0 \
  --envs MYROUNDS=1 \
  --envs DARSHAN_DISABLE=1 \
  --block $COBALT_PARTNAME ${COBALT_CORNER:+--corner} $COBALT_CORNER ${COBALT_SHAPE:+--shape} $COBALT_SHAPE \
  '''

#  --envs PAMID_ASYNC_PROGRESS=1 \
#  --mapping TABCDE \

# simple run command
simple_job = '''ulimit -c 0; runjob \
  --np %(ranks)d \
  --ranks-per-node %(tasks)d \
  --cwd $PWD \
  --envs OMP_NUM_THREADS=%(threads)d \
  --envs XLSMPOPTS=parthds=%(threads)d \
  %(envs)s \
  : %(cmd)s %(options)s
  '''

# MPI run command
mpi_job = '''ulimit -c 0; runjob \
  --np %(ranks)d \
  --ranks-per-node %(tasks)d \
  --cwd $PWD \
  --envs OMP_NUM_THREADS=%(threads)d \
  --envs XLSMPOPTS=parthds=%(threads)d \
  %(envs)s \
  : %(cmd)s %(options)s
  '''

# submission script template
script = None

# submit command
submit = 'qsub --project CloudPredict --nodecount %(nodes)d --time %(hours).2d:%(minutes).2d:00 --outputprefix report.%(label)s --notify %(email)s %(xopts)s --mode script %(jobfile)s'

# timer
timer = 'date; (time -p (%(job)s)) 2>&1 | tee %(timerfile)s'

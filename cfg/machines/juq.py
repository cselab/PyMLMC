
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for JUQUEEN cluster
# IBM BlueGene/Q @ Julich Supercomputing Centre (JSC), Germany
# More information: http://www.fz-juelich.de/ias/jsc/EN/Expertise/Supercomputers/JUQUEEN
# LoadLeveller job scheduling system
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Julich JUQUEEN (IBM BlueGene/Q)'

# JUQUEEN is a cluster
cluster = 1

# default configuration
cores     = 16   # per node
threads   = 4    # per core
walltime  = 1    # hours
memory    = 1024 # GB per core
rack      = 1024 # nodes

# constraints

bootup       = 5   # minutes
min_cores    = 512 * cores
max_cores    = 28 * rack * cores

def min_walltime (cores): # hours
  return 0.5

def max_walltime (cores): # hours
  return 24

# theoretical performance figures per node
peakflops = 12.8 # TFLOP/s
bandwidth = 28.0 # GB/s

# core performance metric (normalized w.r.t. IBM BG/Q)
performance = 1

# scratch path (not required - we use $WORK)
scratch = None

# ensemble support
ensembles = 0

# archive space is not subjec to quota (>100TB should be notified)
archive = '/arch/pra091/pra0913/pymlmc'

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
  '''

#  --envs PAMID_ASYNC_PROGRESS=1 \
#  --mapping TABCDE \

# simple run command
simple_job = '''runjob \
  --np %(ranks)d \
  --ranks-per-node %(tasks)d \
  --cwd $PWD \
  --envs OMP_NUM_THREADS=%(threads)d \
  --envs XLSMPOPTS=parthds=%(threads)d \
  %(envs)s \
  : %(cmd)s
  '''

# MPI run command
mpi_job = '''runjob \
  --np %(ranks)d \
  --ranks-per-node %(tasks)d \
  --cwd $PWD \
  --envs OMP_NUM_THREADS=%(threads)d \
  --envs XLSMPOPTS=parthds=%(threads)d \
  %(envs)s \
  : %(cmd)s
  '''

# submission script template
script = '''
  # @ job_name = %(label)s
  # @ comment = "pymlmc"
  # @ error = report.%(label)s
  # @ output = report.%(label)s
  # @ environment = COPY_ALL
  # @ wall_clock_limit = %(hours).2d:%(minutes).2d:00
  # @ notification = always
  # @ notify_user = %(email)s
  # @ job_type = bluegene
  # @ bg_size = %(nodes)d
  %(xopts)s
  # @ queue
  
  ulimit -c 0
  %(job)s
  '''

# submit command
submit = 'llsubmit %(scriptfile)s'

# timer
timer = '(time -p (%(job)s)) 2>&1 | tee %(timerfile)s'

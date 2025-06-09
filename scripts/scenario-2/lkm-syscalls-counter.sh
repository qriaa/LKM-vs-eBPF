#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-2/perf-data/lkm-syscalls-counter.data
MODULE_FILE=$SCRIPT_DIR/../../lkm/syscalls-counter/syscalls-counter.ko
MODULE_NAME='syscalls_counter'
FUNCTION_NAME='__x64_sys_execve'

#ENTRY_PROBE='raw_syscalls:sys_enter'
#EXIT_PROBE='raw_syscalls:sys_exit'

insmod $MODULE_FILE

# add probes
sudo perf probe --add "$FUNCTION_NAME"
sudo perf probe --add "$FUNCTION_NAME%return"

# -m increases buffer amount, prevents losing chunks
# -e "cycles/call-graph=dwarf/" \
perf record -a -m 16M -o $PERF_RESULTS_PATH \
    -e "cpu-clock/call-graph=dwarf/" \
    -e "probe:$FUNCTION_NAME/call-graph=no/" \
    -e "probe:${FUNCTION_NAME}__return/call-graph=no/" &
PERF_PID=$!
sleep 2

# run workload
for ((i = 0 ; i < 10000 ; i++ )); do
    ls
done

kill -s SIGINT $PERF_PID
wait $PERF_PID

# remove probes
sudo perf probe --del "$FUNCTION_NAME"
sudo perf probe --del "${FUNCTION_NAME}__return"

rmmod $MODULE_NAME

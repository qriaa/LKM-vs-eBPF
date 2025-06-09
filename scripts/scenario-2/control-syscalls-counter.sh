#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-2/perf-data/control-syscalls-counter.data
FUNCTION_NAME='__x64_sys_execve'

# add probes
sudo perf probe --add "$FUNCTION_NAME"
sudo perf probe --add "$FUNCTION_NAME%return"

# -m increases buffer amount, prevents losing chunks
perf record -q -a -m 16M -o $PERF_RESULTS_PATH \
    -e "cpu-clock/call-graph=dwarf/" \
    -e "probe:$FUNCTION_NAME/call-graph=no/" \
    -e "probe:${FUNCTION_NAME}__return/call-graph=no/" &
PERF_PID=$!

# run workload
for ((i = 0 ; i < 10000 ; i++ )); do
    ls
done

kill -s SIGINT $PERF_PID
wait $PERF_PID


#!/usr/bin/env bash

# Ensure sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

FUNCTION_NAME='nf_hook_run_bpf'

sudo ./nf-hook &
EBPF_LOADER_PID=$!

# add probes
sudo perf probe --add "$FUNCTION_NAME"
sudo perf probe --add "$FUNCTION_NAME%return"

iperf3 -s -1 &
IPERF_PID=$!

# -m increases buffer amount, prevents losing chunks
perf record -q -a -g -m 16M -e "cpu-clock/call-graph=dwarf/" -e "probe:$FUNCTION_NAME/call-graph=no/" -e "probe:${FUNCTION_NAME}__return/call-graph=no/" &
PERF_PID=$!

wait $IPERF_PID
kill -s SIGINT $PERF_PID
wait $PERF_PID

# remove probes
sudo perf probe --del "$FUNCTION_NAME"
sudo perf probe --del "${FUNCTION_NAME}__return"

kill -s SIGINT $EBPF_LOADER_PID

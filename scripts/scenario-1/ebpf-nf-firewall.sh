#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-1/perf-data/ebpf-nf-firewall.data
IPERF_CONN_NUM=2
FUNCTION_NAME='net_rx_action'
#FUNCTION_NAME='nf_hook_run_bpf'
EBPF_LOADER_PATH="$SCRIPT_DIR/../../ebpf/nf-firewall/nf-firewall"

sudo $EBPF_LOADER_PATH &
EBPF_LOADER_PID=$!

# add probes
sudo perf probe --add "$FUNCTION_NAME"
sudo perf probe --add "$FUNCTION_NAME%return"

# -m increases buffer amount, prevents losing chunks
perf record -q -a -m 16M -o $PERF_RESULTS_PATH \
    -e "cycles/call-graph=dwarf/" \
    -e "cpu-clock/call-graph=dwarf/" \
    -e "probe:$FUNCTION_NAME/call-graph=no/" \
    -e "probe:${FUNCTION_NAME}__return/call-graph=no/" &
PERF_PID=$!

for ((i=1;i<=IPERF_CONN_NUM;i++)); do
    iperf3 -s -1
done

kill -s SIGINT $PERF_PID
wait $PERF_PID

# remove probes
sudo perf probe --del "$FUNCTION_NAME"
sudo perf probe --del "${FUNCTION_NAME}__return"

kill -s SIGINT $EBPF_LOADER_PID

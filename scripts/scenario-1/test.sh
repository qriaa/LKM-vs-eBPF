#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
PROJ_ROOT=$SCRIPT_DIR/../..

. $PROJ_ROOT/scripts/utils.sh

ensure_sudo

SCENARIO_NAME='scenario-1'

PROBED_FUNCTION='net_rx_action'
PERF_RESULTS_PATH="$PROJ_ROOT/results/scenario-1/perf-data"
mkdir -p $PERF_RESULTS_PATH
IPERF_CONN_NUM=2

workload() {
    for ((i=1;i<=IPERF_CONN_NUM;i++)); do
        iperf3 -s -1
    done
}

# $!, bg jobs and waits must be in the same function, otherwise it doesn't work
run_perf_and_workload() {
    local OUTPUT_PATH="$PERF_RESULTS_PATH/$1.data"

    perf record -q -a -m 16M -o $OUTPUT_PATH \
        -e "cycles/call-graph=dwarf/" \
        -e "cpu-clock/call-graph=dwarf/" \
        -e "probe:${PROBED_FUNCTION}/call-graph=no/" \
        -e "probe:${PROBED_FUNCTION}__return/call-graph=no/" &
    local PERF_PID=$!
    workload
    kill -s SIGINT $PERF_PID
    wait $PERF_PID
}


# Prepare probes
perf probe --add "$PROBED_FUNCTION"
perf probe --add "$PROBED_FUNCTION%return"

TEST="control-firewall"
echo "Running $TEST..."
run_perf_and_workload "$TEST"

TEST="lkm-firewall"
echo "Running $TEST..."
MODULE_FILE=$PROJ_ROOT/lkm/firewall/firewall.ko
MODULE_NAME="firewall"
insmod $MODULE_FILE
run_perf_and_workload "$TEST"
rmmod $MODULE_NAME

TEST="ebpf-nojit-nf-firewall"
echo "Running $TEST..."
EBPF_LOADER="$PROJ_ROOT/ebpf/nf-firewall/nf-firewall"
echo 0 > /proc/sys/net/core/bpf_jit_enable
sudo $EBPF_LOADER &
EBPF_LOADER_PID=$!
run_perf_and_workload "$TEST"
kill -s SIGINT $EBPF_LOADER_PID
wait $EBPF_LOADER_PID
echo 1 > /proc/sys/net/core/bpf_jit_enable

TEST="ebpf-nf-firewall"
echo "Running $TEST..."
EBPF_LOADER="$PROJ_ROOT/ebpf/nf-firewall/nf-firewall"
sudo $EBPF_LOADER &
EBPF_LOADER_PID=$!
run_perf_and_workload "$TEST"
kill -s SIGINT $EBPF_LOADER_PID
wait $EBPF_LOADER_PID

TEST="ebpf-nojit-xdp-firewall"
echo "Running $TEST..."
NET_IF="enp0s25"
EBPF_LOADER="$PROJ_ROOT/ebpf/xdp-firewall/xdp-firewall"
echo 0 > /proc/sys/net/core/bpf_jit_enable
sudo $EBPF_LOADER $NET_IF &
EBPF_LOADER_PID=$!
run_perf_and_workload "$TEST"
kill -s SIGINT $EBPF_LOADER_PID
wait $EBPF_LOADER_PID
echo 1 > /proc/sys/net/core/bpf_jit_enable

TEST="ebpf-xdp-firewall"
echo "Running $TEST..."
NET_IF="enp0s25"
EBPF_LOADER="$PROJ_ROOT/ebpf/xdp-firewall/xdp-firewall"
sudo $EBPF_LOADER $NET_IF &
EBPF_LOADER_PID=$!
run_perf_and_workload "$TEST"
kill -s SIGINT $EBPF_LOADER_PID
wait $EBPF_LOADER_PID

sudo perf probe --del "$PROBED_FUNCTION"
sudo perf probe --del "${PROBED_FUNCTION}__return"

sudo chmod 777 -R $PERF_RESULTS_PATH

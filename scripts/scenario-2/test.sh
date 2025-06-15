#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
PROJ_ROOT=$SCRIPT_DIR/../..

. $SCRIPT_DIR/../utils.sh

ensure_sudo

SCENARIO_NAME='scenario-2'

PERF_RESULTS_PATH="$PROJ_ROOT/results/scenario-2/perf-data"
mkdir -p $PERF_RESULTS_PATH
PROBED_FUNCTIONS=(
    '__x64_sys_execve'
    '__x64_sys_openat'
    '__x64_sys_read'
)

workload() {
    for ((i = 0 ; i < 10000 ; i++ )); do
        ls
    done
}

# $!, bg jobs and waits must be in the same function, otherwise it doesn't work
run_perf_and_workload() {
    local OUTPUT_PATH="$PERF_RESULTS_PATH/$1.data"

    perf record -a -m 32M -o $OUTPUT_PATH \
        -e "cycles/call-graph=dwarf/" \
        -e "cpu-clock/call-graph=dwarf/" \
        -e "probe:__x64_sys_execve/call-graph=no/" \
        -e "probe:__x64_sys_execve__return/call-graph=no/" \
        -e "probe:__x64_sys_openat/call-graph=no/" \
        -e "probe:__x64_sys_openat__return/call-graph=no/" \
        -e "probe:__x64_sys_read/call-graph=no/" \
        -e "probe:__x64_sys_read__return/call-graph=no/" &
    local PERF_PID=$!
    sleep 2
    workload
    kill -s SIGINT $PERF_PID
    wait $PERF_PID
}

for FUNCTION in "${PROBED_FUNCTIONS[@]}"; do
    sudo perf probe --add "$FUNCTION"
    sudo perf probe --add "$FUNCTION%return"
done;

TEST="control-syscalls-counter"
echo "Running $TEST..."
run_perf_and_workload "$TEST"

TEST="lkm-syscalls-counter"
echo "Running $TEST..."
MODULE_FILE=$PROJ_ROOT/lkm/syscalls-counter/syscalls-counter.ko
MODULE_NAME='syscalls_counter'
insmod $MODULE_FILE
run_perf_and_workload "$TEST"
rmmod $MODULE_FILE

TEST="ebpf-nojit-syscalls-counter"
echo "Running $TEST..."
EBPF_LOADER="$PROJ_ROOT/ebpf/syscalls-counter/syscalls-counter"
echo 0 > /proc/sys/net/core/bpf_jit_enable
sudo $EBPF_LOADER &
EBPF_LOADER_PID=$!
run_perf_and_workload "$TEST"
kill -s SIGINT $EBPF_LOADER_PID
wait $EBPF_LOADER_PID
echo 1 > /proc/sys/net/core/bpf_jit_enable

TEST="ebpf-syscalls-counter"
echo "Running $TEST..."
EBPF_LOADER="$PROJ_ROOT/ebpf/syscalls-counter/syscalls-counter"
sudo $EBPF_LOADER &
EBPF_LOADER_PID=$!
run_perf_and_workload "$TEST"
kill -s SIGINT $EBPF_LOADER_PID
wait $EBPF_LOADER_PID

for FUNCTION in "${PROBED_FUNCTIONS[@]}"; do
    sudo perf probe --del "$FUNCTION"
    sudo perf probe --del "${FUNCTION}__return"
done;

sudo chmod 777 -R $PERF_RESULTS_PATH

#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-1/perf-data/lkm-firewall.data
IPERF_CONN_NUM=2
MODULE_FILE=$SCRIPT_DIR/../../lkm/firewall/firewall.ko
MODULE_NAME='firewall'
FUNCTION_NAME='firewall'

insmod $MODULE_FILE

# add probes
sudo perf probe -m $MODULE_NAME --add "$FUNCTION_NAME"
sudo perf probe -m $MODULE_NAME --add "$FUNCTION_NAME%return"

# -m increases buffer amount, prevents losing chunks
perf record -q -a -m 16M -o $PERF_RESULTS_PATH \
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
sudo perf probe -m $MODULE_NAME --del "$FUNCTION_NAME"
sudo perf probe -m $MODULE_NAME --del "${FUNCTION_NAME}__return"

rmmod $MODULE_NAME
